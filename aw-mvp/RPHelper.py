# Note: Functions are not scraping the websites, but rather using the APIs to get the data
#
# Query is a dictionary with the following keys:
# - name: str
# - school: str

def test_print_query(query: dict):
    print(f"Name: {query.get('name', 'Not specified')}")
    print(f"School: {query.get('school', 'Not specified')}")

def test_print_papers(papers: list):
    if not papers:
        print("No papers found.")
        return
        
    print(f"\nFound {len(papers)} papers:")
    print("="*100)
    
    for i, paper in enumerate(papers, 1):
        print(f"\nPaper {i}:")
        print(f"Title: {paper.get('title', 'No title')}")
        
        # Handle authors properly
        authors = paper.get('authors', [])
        if authors:
            author_names = []
            for author in authors:
                if isinstance(author, dict):
                    author_names.append(author.get('name', 'Unknown'))
                else:
                    author_names.append(str(author))
            print(f"Authors: {', '.join(author_names)}")
        else:
            print("Authors: No authors")
            
        print(f"Publication Date: {paper.get('publication_date', 'No date')}")
        
        # Handle categories properly
        categories = paper.get('categories', [])
        if categories:
            print(f"Categories: {', '.join(categories)}")
        else:
            print("Categories: No categories")
            
        print(f"Journal: {paper.get('journal', 'No journal')}")
        
        # Handle different link types
        if 'links' in paper:
            links = paper['links']
            if 'arxiv_id' in links:
                print(f"arXiv ID: {links.get('arxiv_id', 'No ID')}")
            elif 'pmid' in links:
                print(f"PubMed ID: {links.get('pmid', 'No ID')}")
            elif 'scholar_id' in links:
                print(f"Scholar ID: {links.get('scholar_id', 'No ID')}")
            
            # Print DOI if available
            if 'doi' in links:
                print(f"DOI: {links.get('doi', 'No DOI')}")
            print(f"Abstract: {links.get('abstract', 'No abstract link')}")
        
        # Print abstract if available
        if paper.get('abstract'):
            abstract = paper['abstract']
            if len(abstract) > 200:
                abstract = abstract[:200] + "..."
            print(f"Abstract: {abstract}")
            
        print("-"*100)

def get_papers(query: dict):
    # ================================
    # Example of papers returned by this function
    # [
    #     {
    #         "title": "Attention Is All You Need",
    #         "authors": [
    #             {"name": "Ashish Vaswani", "affiliation": "Google Brain"},
    #             {"name": "Noam Shazeer", "affiliation": "Google Brain"},
    #             {"name": "Niki Parmar", "affiliation": "Google Brain"},
    #             {"name": "Jakob Uszkoreit", "affiliation": "Google Research"},
    #             {"name": "Llion Jones", "affiliation": "Google Brain"},
    #             {"name": "Aidan N. Gomez", "affiliation": "University of Toronto"},
    #             {"name": "Łukasz Kaiser", "affiliation": "Google Brain"},
    #             {"name": "Illia Polosukhin", "affiliation": "Google Research"}
    #         ],
    #         "publication_date": "2017-06-12T00:00:00Z",
    #         "categories": ["cs.CL", "cs.AI", "cs.LG"],
    #         "journal": "arXiv",
    #         "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely...",
    #         "links": {
    #             "doi": "10.48550/arXiv.1706.03762",
    #             "pdf": "https://arxiv.org/pdf/1706.03762",
    #             "abstract": "https://arxiv.org/abs/1706.03762",
    #             "arxiv_id": "1706.03762"
    #         }
    #     },
    #     {
    #         "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    #         "authors": [
    #             {"name": "Jacob Devlin", "affiliation": "Google AI Language"},
    #             {"name": "Ming-Wei Chang", "affiliation": "Google AI Language"},
    #             {"name": "Kenton Lee", "affiliation": "Google AI Language"},
    #             {"name": "Kristina Toutanova", "affiliation": "Google AI Language"}
    #         ],
    #         "publication_date": "2018-10-11T00:00:00Z",
    #         "categories": ["cs.CL", "cs.AI"],
    #         "journal": "arXiv",
    #         "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers...",
    #         "links": {
    #             "doi": "10.48550/arXiv.1810.04805",
    #             "pdf": "https://arxiv.org/pdf/1810.04805",
    #             "abstract": "https://arxiv.org/abs/1810.04805",
    #             "arxiv_id": "1810.04805"
    #         }
    #     }
    # ]
    # Note: Some sources (DOAJ, Zenodo) may include an "id" field, but not useful
    # ================================
    
    # ================================
    # Parse Query
    # ================================
    name: str | None = query.get('name', None)
    school: str | None = query.get('school', None)
    test_print_query(query)

    # ================================
    # Get Papers
    # ================================
    # Papers
    # title, authors, links, publication date, and categories
    # ================================
    papers = []
    papers.extend(get_papers_from_arxiv(name, school) or [])
    papers.extend(get_papers_from_pubmed(name, school) or [])
    papers.extend(get_papers_from_doaj(name, school) or [])
    papers.extend(get_papers_from_zenodo(name, school) or [])
    papers.extend(get_papers_from_crossref(name, school) or [])
    
    # print(f"\nTotal papers found before deduplication: {len(papers)}")
    
    # Deduplicate papers based on DOI first, then title
    papers = deduplicate_papers(papers)
    
    # print(f"Total unique papers after deduplication: {len(papers)}") 
    return papers

def parse_arxiv_response(response: str, target_author: str | None = None):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": [
    #             {"name": "Author 1", "affiliation": "Affiliation 1"},
    #             {"name": "Author 2", "affiliation": "Affiliation 2"}
    #         ],
    #         "links": { ... },
    #         "publication_date": "2023-01-01T00:00:00Z",
    #         "categories": ["cs.CV", "cs.AI"],
    #         "journal": "arXiv",
    #         "abstract": "Paper abstract text"
    #     }
    # }
    # ================================
    import xml.etree.ElementTree as ET
    papers = []
    try:
        root = ET.fromstring(response)
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
        }
        for entry in root.findall('.//atom:entry', namespaces):
            authors = []
            author_found = False
            for author_elem in entry.findall('atom:author', namespaces):
                name_elem = author_elem.find('atom:name', namespaces)
                aff_elem = author_elem.find('arxiv:affiliation', namespaces)
                author_name = name_elem.text.strip() if name_elem is not None and name_elem.text else ''
                author_affiliation = aff_elem.text.strip() if aff_elem is not None and aff_elem.text else ''
                if author_name:
                    authors.append({"name": author_name, "affiliation": author_affiliation})
                    if target_author and target_author.lower() in author_name.lower():
                        author_found = True

            if target_author and not author_found:
                continue

            paper = {}
            paper['authors'] = authors
            title_elem = entry.find('atom:title', namespaces)
            if title_elem is not None and title_elem.text is not None:
                paper['title'] = title_elem.text.strip()
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is not None and id_elem.text is not None:
                arxiv_id = id_elem.text.split('/')[-1]
                paper['links'] = {
                    'pdf': f"https://arxiv.org/pdf/{arxiv_id}",
                    'abstract': f"https://arxiv.org/abs/{arxiv_id}",
                    'arxiv_id': arxiv_id
                }
            doi_elem = entry.find('arxiv:doi', namespaces)
            if doi_elem is not None and doi_elem.text is not None:
                paper['links']['doi'] = doi_elem.text.strip()
            published_elem = entry.find('atom:published', namespaces)
            if published_elem is not None:
                paper['publication_date'] = published_elem.text
            categories = []
            for category in entry.findall('atom:category', namespaces):
                cat_term = category.get('term')
                if cat_term:
                    categories.append(cat_term)
            paper['categories'] = categories
            # arXiv does not have a journal, but for consistency:
            paper['journal'] = 'arXiv'
            # Get abstract
            summary_elem = entry.find('atom:summary', namespaces)
            if summary_elem is not None and summary_elem.text:
                paper['abstract'] = summary_elem.text.strip()
            papers.append(paper)
        return papers
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    except Exception as e:
        print(f"Error processing arXiv response: {e}")
        return []
      
def get_papers_from_arxiv(name: str | None = None, school: str | None = None):
    import urllib.parse
    import requests

    if not name:
        print("No author name provided")
        return []

    # Use more specific search terms
    search_strategies = [
        f'au:"{name}"',  # Exact match with quotes
        f'au:{name}',    # Standard author search
    ]
    
    if school:
        # Add school affiliation search
        search_strategies.append(f'au:"{name}" AND aff:"{school}"')
        search_strategies.append(f'au:{name} OR aff:{school}')

    all_papers = []
    
    for search_query in search_strategies:
        # print(f"Trying search: {search_query}")
        
        encoded_search_terms = urllib.parse.quote(search_query)
        url = f"http://export.arxiv.org/api/query?search_query={encoded_search_terms}&max_results=100"

        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the XML response
            papers = parse_arxiv_response(response.text, name)
            
            # print(f"Found {len(papers)} papers for search '{search_query}'")
            all_papers.extend(papers)
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error for search '{search_query}': {e}")
            continue
    
    return all_papers

def parse_pubmed_response(response: str, target_author: str):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": [
    #             {"name": "Author 1", "affiliation": "Affiliation 1"},
    #             {"name": "Author 2", "affiliation": "Affiliation 2"}
    #         ],
    #         "links": { ... },
    #         "publication_date": "2023-01-01",
    #         "categories": ["MeSH Term 1", "MeSH Term 2"],
    #         "journal": "Journal Name",
    #         "abstract": "Paper abstract text"
    #     }
    # }
    # ================================
    import xml.etree.ElementTree as ET
    papers = []
    try:
        root = ET.fromstring(response)
        for article in root.findall('.//PubmedArticle'):
            authors = []
            author_found = False
            for author in article.findall('.//Author'):
                last_name_elem = author.find('LastName')
                first_name_elem = author.find('ForeName')
                aff_elem = author.find('AffiliationInfo/Affiliation')
                last_name = last_name_elem.text.strip() if last_name_elem is not None and last_name_elem.text else ''
                first_name = first_name_elem.text.strip() if first_name_elem is not None and first_name_elem.text else ''
                full_name = f"{first_name} {last_name}".strip()
                affiliation = aff_elem.text.strip() if aff_elem is not None and aff_elem.text else ''
                if full_name:
                    authors.append({"name": full_name, "affiliation": affiliation})
                    if target_author.lower() in full_name.lower():
                        author_found = True
            if not author_found:
                continue
            paper = {}
            paper['authors'] = authors
            pmid_elem = article.find('.//PMID')
            if pmid_elem is not None and pmid_elem.text:
                pmid = pmid_elem.text
                paper['links'] = {
                    'pmid': pmid,
                    'abstract': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'pdf': None
                }
            doi_elem = article.find('.//ELocationID[@EIdType="doi"]')
            if doi_elem is not None and doi_elem.text:
                paper['links']['doi'] = doi_elem.text.strip()
            title_elem = article.find('.//ArticleTitle')
            if title_elem is not None and title_elem.text:
                paper['title'] = title_elem.text.strip()
            pub_date_elem = article.find('.//PubDate')
            if pub_date_elem is not None:
                year_elem = pub_date_elem.find('Year')
                month_elem = pub_date_elem.find('Month')
                day_elem = pub_date_elem.find('Day')
                date_parts = []
                if year_elem is not None and year_elem.text:
                    date_parts.append(year_elem.text)
                if month_elem is not None and month_elem.text:
                    date_parts.append(month_elem.text)
                if day_elem is not None and day_elem.text:
                    date_parts.append(day_elem.text)
                if date_parts:
                    paper['publication_date'] = '-'.join(date_parts)
            journal_elem = article.find('.//Journal/Title')
            if journal_elem is not None and journal_elem.text:
                paper['journal'] = journal_elem.text.strip()
            abstract_elem = article.find('.//Abstract/AbstractText')
            if abstract_elem is not None and abstract_elem.text:
                paper['abstract'] = abstract_elem.text.strip()
            categories = []
            for mesh_elem in article.findall('.//MeshHeadingList/MeshHeading/DescriptorName'):
                if mesh_elem.text:
                    categories.append(mesh_elem.text.strip())
            paper['categories'] = categories
            papers.append(paper)
        return papers
    except ET.ParseError as e:
        print(f"Error parsing PubMed XML: {e}")
        return []
    except Exception as e:
        print(f"Error processing PubMed response: {e}")
        return []

def get_papers_from_pubmed(name: str | None = None, school: str | None = None):
    import requests
    import time
    import xml.etree.ElementTree as ET
    
    if not name:
        print("No author name provided for PubMed search")
        return []
    
    # NCBI API base URL
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Search strategies for PubMed
    search_strategies = [
        f'"{name}"[Author]',  # Exact name match
        f'{name}[Author]',    # Standard author search
    ]
    
    if school:
        # Add school affiliation search
        search_strategies.append(f'"{name}"[Author] AND "{school}"[Affiliation]')
        search_strategies.append(f'{name}[Author] AND {school}[Affiliation]')
    
    all_papers = []
    
    for search_query in search_strategies:
        # print(f"PubMed search: {search_query}")
        
        try:
            # Search for papers and get PMIDs
            search_params = {
                'db': 'pubmed',
                'term': search_query,
                'retmax': 100,  # Maximum results
                'retmode': 'xml',
                'usehistory': 'y'
            }
            
            search_url = base_url + "esearch.fcgi"  # esearch.fcgi is endpoint for searching PubMed
            search_response = requests.get(search_url, params=search_params)
            search_response.raise_for_status()
            
            # Parse search results to get PMIDs
            search_root = ET.fromstring(search_response.text)
            pmids = []
            
            # Extract PMIDs from search results
            for id_elem in search_root.findall('.//Id'):
                if id_elem.text:
                    pmids.append(id_elem.text)
            
            if not pmids:
                print(f"No papers found for search: {search_query}")
                continue
            
            # print(f"Found {len(pmids)} papers for search: {search_query}")
            
            # Fetch detailed information for each paper
            batch_size = 20
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                
                fetch_params = {
                    'db': 'pubmed',
                    'id': ','.join(batch_pmids),
                    'retmode': 'xml',
                    'rettype': 'abstract'
                }
                
                fetch_url = base_url + "efetch.fcgi"
                fetch_response = requests.get(fetch_url, params=fetch_params)
                fetch_response.raise_for_status()
                
                # Parse paper details
                papers = parse_pubmed_response(fetch_response.text, name)
                all_papers.extend(papers)
                
                # NCBI's rate limiting (3 requests per second)
                time.sleep(0.35)
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error for PubMed search '{search_query}': {e}")
            continue
        except ET.ParseError as e:
            print(f"XML Parse Error for PubMed search '{search_query}': {e}")
            continue
    
    return all_papers

def parse_doaj_response(data: dict, target_author: str | None = None, target_school: str | None = None):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": [
    #             {"name": "Author 1", "affiliation": "Affiliation 1"},
    #             {"name": "Author 2", "affiliation": "Affiliation 2"}
    #         ],
    #         "links": { ... },
    #         "publication_date": "2023-01-01",
    #         "categories": ["Keyword1", "Keyword2"],
    #         "journal": "Journal Name",
    #         "abstract": "Paper abstract text"
    #     }
    # }
    # ================================
    papers = []
    
    try:
        for article in data.get('results', []):
            bibjson = article.get('bibjson', {})
            
            # Check if the target author is in the authors list
            authors = []
            author_found = False
            school_found = False
            
            for author in bibjson.get('author', []):
                author_name = author.get('name', '').strip()
                author_affiliation = author.get('affiliation', '').strip()
                
                if author_name:
                    authors.append({"name": author_name, "affiliation": author_affiliation})
                    
                    # Check if this author matches our target
                    if target_author and target_author.lower() in author_name.lower():
                        author_found = True
                    
                    # Check if school/affiliation matches
                    if target_school and target_school.lower() in author_affiliation.lower():
                        school_found = True
            
            # Only process this paper if the target author is found (or if no target specified)
            if target_author and not author_found:
                continue
            
            # If school is specified, check if any author has that affiliation
            if target_school and not school_found:
                continue
            
            # Extract paper details
            paper = {}
            paper['authors'] = authors
            paper['id'] = article.get('id', '')
            
            # Get title
            paper['title'] = bibjson.get('title', 'No title')
            
            # Get publication date
            year = bibjson.get('year', '')
            month = bibjson.get('month', '')
            if year:
                if month:
                    paper['publication_date'] = f"{year}-{month.zfill(2)}"
                else:
                    paper['publication_date'] = year
            
            # Get journal information
            journal = bibjson.get('journal', {})
            paper['journal'] = journal.get('title', 'No journal')
            
            # Get abstract
            paper['abstract'] = bibjson.get('abstract', '')
            
            # Get keywords
            paper['categories'] = bibjson.get('keywords', [])
            
            # Get links
            links = {}
            
            # Get DOI from identifiers
            for identifier in bibjson.get('identifier', []):
                if identifier.get('type') == 'doi':
                    links['doi'] = identifier.get('id', '')
                elif identifier.get('type') == 'eissn':
                    links['eissn'] = identifier.get('id', '')
                elif identifier.get('type') == 'pissn':
                    links['pissn'] = identifier.get('id', '')
            
            # Get fulltext links
            for link in bibjson.get('link', []):
                if link.get('type') == 'fulltext':
                    if link.get('content_type') == 'pdf':
                        links['pdf'] = link.get('url', '')
                    else:
                        links['abstract'] = link.get('url', '')
            
            paper['links'] = links
            
            papers.append(paper)
        
        return papers
        
    except Exception as e:
        print(f"Error parsing DOAJ response: {e}")
        return []

def get_papers_from_doaj(name: str | None = None, school: str | None = None):
    import requests
    import urllib.parse
    import time
    
    if not name:
        print("No author name provided for DOAJ search")
        return []
    
    # DOAJ API base URL
    base_url = "https://doaj.org/api/search/articles"
    
    # Search strategies for DOAJ
    search_strategies = [
        name,  # Simple name search
        f'"{name}"',  # Exact name match
    ]
    
    if school:
        # Add school affiliation search
        search_strategies.append(f'{name} {school}')
        search_strategies.append(f'"{name}" "{school}"')
    
    all_papers = []
    
    for search_query in search_strategies:
        # print(f"DOAJ search: {search_query}")
        
        try:
            # Search for papers - DOAJ uses path-based search
            url = f"{base_url}/{urllib.parse.quote(search_query)}"
            params = {
                'page': 1,
                'pageSize': 100  # Maximum page size
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('total', 0) == 0:
                print(f"No papers found for search: {search_query}")
                continue
            
            # print(f"Found {data.get('total', 0)} papers for search: {search_query}")
            
            # Parse the results
            papers = parse_doaj_response(data, name, school)
            all_papers.extend(papers)
            
            # Handle pagination if there are more results
            total_pages = (data.get('total', 0) + 99) // 100  # Ceiling division
            for page in range(2, min(total_pages + 1, 6)):  # Limit to 5 pages max
                params['page'] = page
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                papers = parse_doaj_response(data, name, school)
                all_papers.extend(papers)
                
                # Rate limiting
                time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error for DOAJ search '{search_query}': {e}")
            continue
        except Exception as e:
            print(f"Error processing DOAJ search '{search_query}': {e}")
            continue
    
    # print(f"Total DOAJ papers found: {len(all_papers)}")
    
    return all_papers

def parse_zenodo_response(data: dict, target_author: str | None = None, target_school: str | None = None):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": [
    #             {"name": "Author 1", "affiliation": "Affiliation 1"},
    #             {"name": "Author 2", "affiliation": "Affiliation 2"}
    #         ],
    #         "links": { ... },
    #         "publication_date": "2023-01-01T00:00:00Z",
    #         "categories": ["Keyword1", "Keyword2"],
    #         "journal": "Journal Name",
    #         "abstract": "Paper abstract text"
    #     }
    # }
    # ================================
    papers = []
    
    try:
        hits = data.get('hits', {}).get('hits', [])
        
        for record in hits:
            meta = record.get('metadata', {})
            
            # authors
            authors = []
            author_found = False
            school_found = False
            
            for creator in meta.get('creators', []):
                # handle both person_or_org and legacy creator formats
                if 'person_or_org' in creator:
                    author_name = creator['person_or_org'].get('name', '')
                    if author_name is None:
                        author_name = ''
                    else:
                        author_name = author_name.strip()
                    
                    author_affiliation = ''
                    if 'affiliation' in creator and creator['affiliation']:
                        affiliation_name = creator['affiliation'].get('name', '')
                        if affiliation_name is not None:
                            author_affiliation = affiliation_name.strip()
                else:
                    author_name = creator.get('name', '')
                    if author_name is None:
                        author_name = ''
                    else:
                        author_name = author_name.strip()
                    
                    author_affiliation = ''
                    if 'affiliation' in creator:
                        affiliation = creator['affiliation']
                        if affiliation is not None:
                            author_affiliation = affiliation.strip()
                
                authors.append({"name": author_name, "affiliation": author_affiliation})
                
                # check if this author matches our target (handle "Last, First" format)
                if target_author:
                    # try direct match first
                    if target_author.lower() in author_name.lower():
                        author_found = True
                    else:
                        # try matching last name (before comma) or first name (after comma)
                        name_parts = target_author.split()
                        if len(name_parts) >= 2:
                            last_name = name_parts[-1]  # Last part is last name
                            first_name = ' '.join(name_parts[:-1])  # Everything else is first name
                            # check if last name matches (before comma in Zenodo format)
                            if ',' in author_name:
                                zenodo_last_name = author_name.split(',')[0].strip()
                                if last_name.lower() in zenodo_last_name.lower():
                                    author_found = True
                            # also check if full name matches
                            if target_author.lower() in author_name.lower():
                                author_found = True
                        else:
                            # single name - check if it matches any part
                            if target_author.lower() in author_name.lower():
                                author_found = True
                
                if target_school and target_school.lower() in author_affiliation.lower():
                    school_found = True
            
            # only process this paper if the target author is found (or if no target specified)
            if target_author and not author_found:
                continue
            
            # if school is specified, check if any author has that affiliation
            if target_school and not school_found:
                continue
            
            # extract paper details
            paper = {}
            paper['authors'] = authors
            paper['id'] = record.get('id', '')
            
            # get title
            paper['title'] = meta.get('title', 'No title')
            if paper['title'] is None:
                paper['title'] = 'No title'
            
            # get publication date
            pub_date = meta.get('publication_date') or meta.get('created')
            paper['publication_date'] = pub_date if pub_date else ''
            
            # get journal information
            journal = meta.get('journal', {})
            if isinstance(journal, dict) and journal:
                paper['journal'] = journal.get('title', 'Zenodo')
                if paper['journal'] is None:
                    paper['journal'] = 'Zenodo'
            else:
                paper['journal'] = 'Zenodo'
            
            # get abstract/description
            paper['abstract'] = meta.get('description', '')
            if paper['abstract'] is None:
                paper['abstract'] = ''
            
            # Get keywords/categories
            paper['categories'] = meta.get('keywords', [])
            if paper['categories'] is None:
                paper['categories'] = []
            
            # get links
            links = {}
            
            # get DOI
            if 'doi' in meta:
                links['doi'] = meta['doi']
            
            # get PDF links from files
            if 'files' in record:
                for f in record['files']:
                    if f.get('type') == 'pdf' or (f.get('key', '').endswith('.pdf')):
                        links['pdf'] = f.get('links', {}).get('self', f.get('links', {}).get('download', ''))
            
            # get abstract link
            if 'doi' in links:
                links['abstract'] = f"https://doi.org/{links['doi']}"
            elif 'id' in record:
                links['abstract'] = f"https://zenodo.org/record/{record['id']}"
            
            paper['links'] = links
            
            papers.append(paper)
        
        return papers
        
    except Exception as e:
        print(f"Error parsing Zenodo response: {e}")
        return []

def get_papers_from_zenodo(name: str | None = None, school: str | None = None):
    import requests
    import time
    
    if not name:
        print("No author name provided for Zenodo search")
        return []
    
    # Zenodo API base URL
    base_url = "https://zenodo.org/api/records"
    
    # Zenodo search by creator name (exact phrase)
    # Zenodo uses "Last, First" format for author names
    search_strategies = [
        f'metadata.creators.person_or_org.name:"{name}"',
        f'"{name}"',
    ]
    
    if school:
        # Add school affiliation search
        search_strategies.append(f'metadata.creators.person_or_org.name:"{name}" AND metadata.creators.person_or_org.affiliation:"{school}"')
        search_strategies.append(f'"{name}" "{school}"')
    
    all_papers = []
    
    for search_query in search_strategies:
        # print(f"Zenodo search: {search_query}")
        
        try:
            # search for papers
            params = {
                'q': search_query,
                'size': 100,  # max per page
                'page': 1,
                'sort': 'mostrecent',
            }
            
            for page in range(1, 6):  # get top 5 pages
                params['page'] = page
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # debug: print response structure
                if page == 1:
                    # print(f"Zenodo API response keys: {list(data.keys())}")
                    if 'hits' in data:
                        # print(f"Hits keys: {list(data['hits'].keys())}")
                        # print(f"Total hits: {data['hits'].get('total', 0)}")
                        pass
                
                # parse the results
                papers = parse_zenodo_response(data, name, school)
                all_papers.extend(papers)
                
                # check if we need to continue to next page
                hits = data.get('hits', {}).get('hits', [])
                if not hits:
                    if page == 1:
                        # print(f"No papers found for search: {search_query}")
                        pass
                    break
                
                # if less than 100 results, no more pages
                if len(hits) < 100:
                    break
                
                # rate limiting
                time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error for Zenodo search '{search_query}': {e}")
            continue
        except Exception as e:
            print(f"Error processing Zenodo search '{search_query}': {e}")
            continue
    
    # print(f"Total Zenodo papers found: {len(all_papers)}")
    
    return all_papers

def parse_crossref_response(data: dict, target_author: str | None = None, target_school: str | None = None):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": [
    #             {"name": "Author 1", "affiliation": "Affiliation 1"},
    #             {"name": "Author 2", "affiliation": "Affiliation 2"}
    #         ],
    #         "links": { ... },
    #         "publication_date": "2023-01-01",
    #         "categories": ["Keyword1", "Keyword2"],
    #         "journal": "Journal Name",
    #         "abstract": "Paper abstract text"
    #     }
    # }
    # ================================
    papers = []
    
    try:
        items = data.get('message', {}).get('items', [])
        
        for item in items:
            # check if the target author is in the authors list
            authors = []
            author_found = False
            school_found = False
            
            for author in item.get('author', []):
                # handle different author name formats
                given_name = author.get('given', '').strip()
                family_name = author.get('family', '').strip()
                author_name = f"{given_name} {family_name}".strip()
                author_affiliation = ''
                
                # get affiliation from author object
                if 'affiliation' in author and author['affiliation']:
                    affiliations = []
                    for aff in author['affiliation']:
                        if isinstance(aff, dict) and 'name' in aff:
                            affiliations.append(aff['name'].strip())
                        elif isinstance(aff, str):
                            affiliations.append(aff.strip())
                    author_affiliation = '; '.join(affiliations)
                
                if author_name:
                    authors.append({"name": author_name, "affiliation": author_affiliation})
                    
                    # precise author matching
                    if target_author:
                        target_lower = target_author.lower().strip()
                        author_lower = author_name.lower().strip()
                        
                        # check for exact match
                        if target_lower == author_lower:
                            author_found = True
                        
                        # check for "Last, First" format match
                        elif ',' in author_lower:
                            # if author is "B, A" and target is "A B"
                            author_parts = author_lower.split(',')
                            if len(author_parts) == 2:
                                last_name = author_parts[0].strip()
                                first_name = author_parts[1].strip()
                                reversed_author = f"{first_name} {last_name}"
                                if target_lower == reversed_author:
                                    author_found = True
                        
                        # check for "Last First" format (no comma, like "A B")
                        elif len(author_lower.split()) == 2:
                            author_parts = author_lower.split()
                            target_parts = target_lower.split()
                            if len(target_parts) == 2:
                                # check if names match in either order
                                if (author_parts[0] == target_parts[0] and author_parts[1] == target_parts[1]) or \
                                   (author_parts[0] == target_parts[1] and author_parts[1] == target_parts[0]):
                                    author_found = True
                        
                        # check for initials format (e.g., "P. A" vs "A P")
                        elif '.' in author_lower and len(target_lower.split()) >= 2:
                            # if author is "P. A" and target is "A P"
                            author_parts = author_lower.split()
                            target_parts = target_lower.split()
                            
                            if len(author_parts) == 2 and len(target_parts) >= 2:
                                # check if first part is initial and last names match
                                if (author_parts[0].endswith('.') and 
                                    author_parts[0][0] == target_parts[0][0] and 
                                    author_parts[1] == target_parts[-1]):
                                    author_found = True
                        
                        # very strict matching - only exact name parts, no partial matches  
                        else:
                            target_parts = target_lower.split()
                            author_parts = author_lower.split()
                            
                            # Only match if we have exactly the same name parts
                            if len(target_parts) == 2 and len(author_parts) == 2:
                                # Both parts must match exactly (in either order)
                                if (target_parts[0] == author_parts[0] and target_parts[1] == author_parts[1]) or \
                                   (target_parts[0] == author_parts[1] and target_parts[1] == author_parts[0]):
                                    author_found = True
                    
                    # check if school/affiliation matches
                    if target_school and target_school.lower() in author_affiliation.lower():
                        school_found = True
            
            # only process this paper if the target author is found (or if no target specified)
            if target_author and not author_found:
                continue
            
            # if school is specified, check if any author has that affiliation
            if target_school and not school_found:
                continue
            
            # extract paper details
            paper = {}
            paper['authors'] = authors
            
            # get title
            title_parts = []
            for title in item.get('title', []):
                if title:
                    title_parts.append(title.strip())
            paper['title'] = ' '.join(title_parts) if title_parts else 'No title'
            
            # get publication date
            pub_date = item.get('published-print', {}).get('date-parts', [[]])[0]
            if pub_date:
                if len(pub_date) >= 3:
                    paper['publication_date'] = f"{pub_date[0]}-{str(pub_date[1]).zfill(2)}-{str(pub_date[2]).zfill(2)}"
                elif len(pub_date) >= 2:
                    paper['publication_date'] = f"{pub_date[0]}-{str(pub_date[1]).zfill(2)}"
                elif len(pub_date) >= 1:
                    paper['publication_date'] = str(pub_date[0])
            
            # get journal information
            container = item.get('container-title', [])
            paper['journal'] = container[0] if container else 'No journal'
            
            # get abstract
            abstract = item.get('abstract', '')
            if abstract:
                paper['abstract'] = abstract.strip()
            else:
                paper['abstract'] = ''
            
            # get keywords/subject categories
            paper['categories'] = item.get('subject', [])
            
            # get links
            links = {}
            
            # get DOI
            doi = item.get('DOI', '')
            if doi:
                links['doi'] = doi
                links['abstract'] = f"https://doi.org/{doi}"
            
            # get PDF links if available
            if 'link' in item:
                for link in item['link']:
                    if link.get('content-type') == 'application/pdf':
                        links['pdf'] = link.get('URL', '')
                    elif link.get('intended-application') == 'text-mining':
                        links['fulltext'] = link.get('URL', '')
            
            paper['links'] = links
            
            papers.append(paper)
        
        return papers
        
    except Exception as e:
        print(f"Error parsing Crossref response: {e}")
        return []

def get_papers_from_crossref(name: str | None = None, school: str | None = None):
    import requests
    import urllib.parse
    
    if not name:
        print("No author name provided for Crossref search")
        return []
    
    # crossref API base URL
    base_url = "https://api.crossref.org/works"
    
    # simple query using query.author parameter
    search_query = name.replace(' ', '+')  # replace spaces with + for URL encoding
    
    # print(f"Crossref search: query.author={search_query}")
    
    try:
        # make the API request
        url = f"{base_url}?query.author={search_query}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # parse the results
        papers = parse_crossref_response(data, name, school)
        
        # print(f"Found {len(papers)} papers from Crossref")
        return papers
        
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error for Crossref search: {e}")
        return []
    except Exception as e:
        print(f"Error processing Crossref search: {e}")
        return []

def deduplicate_papers(papers: list) -> list:
    # check if papers is empty
    if not papers:
        return []
    
    # group papers by DOI first, then by title
    doi_groups = {}
    title_groups = {}
    
    for paper in papers:
        # try to group by DOI first
        doi = None
        if 'links' in paper and 'doi' in paper['links']:
            doi = paper['links']['doi'].lower().strip()
        
        if doi:
            if doi not in doi_groups:
                doi_groups[doi] = []
            doi_groups[doi].append(paper)
        else:
            # if no DOI, group by title
            title = paper.get('title', '').lower().strip()
            if title and title != 'no title':
                if title not in title_groups:
                    title_groups[title] = []
                title_groups[title].append(paper)
            else:
                # if no title either, treat as unique
                if 'no_title_group' not in title_groups:
                    title_groups['no_title_group'] = []
                title_groups['no_title_group'].append(paper)
    
    # merge papers within each group
    unique_papers = []
    
    # process DOI groups first
    for doi, group in doi_groups.items():
        if len(group) == 1:
            unique_papers.append(group[0])
        else:
            # merge multiple papers with same DOI
            merged_paper = merge_paper_group(group)
            unique_papers.append(merged_paper)
    
    # process title groups
    for title, group in title_groups.items():
        if title == 'no_title_group':
            # add papers without title as-is
            unique_papers.extend(group)
        elif len(group) == 1:
            unique_papers.append(group[0])
        else:
            # merge multiple papers with same title
            merged_paper = merge_paper_group(group)
            unique_papers.append(merged_paper)
    return unique_papers

def merge_paper_group(papers: list) -> dict:
    # check if papers is empty
    if not papers:
        return {}
    
    if len(papers) == 1:
        return papers[0]
    
    # start with the first paper as base
    merged = papers[0].copy()
    
    for paper in papers[1:]:
        # merge authors - combine unique authors with affiliations
        if 'authors' in paper and paper['authors']:
            if 'authors' not in merged:
                merged['authors'] = []
            
            existing_authors = {author['name'].lower(): author for author in merged['authors']}
            
            for author in paper['authors']:
                author_name_lower = author['name'].lower()
                if author_name_lower in existing_authors:
                    # author exists, merge affiliations if available
                    existing_author = existing_authors[author_name_lower]
                    if not existing_author.get('affiliation') and author.get('affiliation'):
                        existing_author['affiliation'] = author['affiliation']
                else:
                    # new author, add to list
                    merged['authors'].append(author)
        
        # merge links - preserve all available links
        if 'links' in paper and paper['links']:
            if 'links' not in merged:
                merged['links'] = {}
            
            for link_type, link_value in paper['links'].items():
                if link_value and (link_type not in merged['links'] or not merged['links'][link_type]):
                    merged['links'][link_type] = link_value
        
        # merge categories/keywords - combine unique categories
        if 'categories' in paper and paper['categories']:
            if 'categories' not in merged:
                merged['categories'] = []
            
            existing_categories = set(cat.lower() for cat in merged['categories'])
            for category in paper['categories']:
                if category.lower() not in existing_categories:
                    merged['categories'].append(category)
        
        # merge other fields - prefer non-empty values
        for field in ['title', 'journal', 'abstract', 'publication_date']:
            if field in paper and paper[field] and (field not in merged or not merged[field]):
                merged[field] = paper[field]

    return merged