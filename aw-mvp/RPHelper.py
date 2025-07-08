# Note: Functions are not scraping the websites, but rather using the APIs to get the data
# arXiv: https://arxiv.org/
# PubMed: https://pubmed.ncbi.nlm.nih.gov/
# Google Scholar: https://scholar.google.com/
# DOAJ: https://doaj.org/
# Semantic Scholar: https://www.semanticscholar.org/
# Zenodo: https://zenodo.org/
# Crossref: https://www.crossref.org/
#
# Query is a dictionary with the following keys:
# - name: str
# - school: str


def test_print_query(query: dict):
    print(f"Name: {query['name']}")
    print(f"School: {query['school']}")

def test_print_papers(papers: list):
    if not papers:
        print("No papers found.")
        return
        
    print(f"\nFound {len(papers)} papers:")
    print("="*100)
    
    for i, paper in enumerate(papers, 1):
        print(f"\nPaper {i}:")
        print(f"Title: {paper.get('title', 'No title')}")
        print(f"Authors: {', '.join(paper.get('authors', ['No authors']))}")
        print(f"Publication Date: {paper.get('publication_date', 'No date')}")
        print(f"Categories: {', '.join(paper.get('categories', ['No categories']))}")
        if 'links' in paper:
            print(f"arXiv ID: {paper['links'].get('arxiv_id', 'No ID')}")
            print(f"Abstract: {paper['links'].get('abstract', 'No abstract link')}")
        print("-"*100)

def get_papers(query: dict):
    # ================================
    # Parse Query
    # ================================
    name: str | None = query.get('name', None)
    school: str | None = query.get('school', None)
    test_print_query(query)
    pass

    # ================================
    # Get Papers
    # ================================
    # Papers
    # title, authors, links, publication date, and categories
    # ================================
    papers = []
    papers.extend(get_papers_from_arxiv(name, school))
    papers.extend(get_papers_from_pubmed(name, school) or [])
    papers.extend(get_papers_from_google_scholar(name, school) or [])
    papers.extend(get_papers_from_doaj(name, school) or [])
    papers.extend(get_papers_from_semantic_scholar(name, school) or [])
    papers.extend(get_papers_from_zenodo(name, school) or [])
    papers.extend(get_papers_from_crossref(name, school) or [])
    test_print_papers(papers)
    pass

    # ================================
    # Get Keywords/Topics
    # ================================
    pass

def parse_arxiv_response(response: str, target_author: str | None = None):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": ["Author 1", "Author 2"],
    #         "links": {
    #             "pdf": "https://arxiv.org/pdf/1234.5678",
    #             "abstract": "https://arxiv.org/abs/1234.5678",
    #             "arxiv_id": "1234.5678"
    #         },
    #         "publication_date": "2023-01-01T00:00:00Z",
    #         "categories": ["cs.CV", "cs.AI"]
    #     }
    # }
    # ================================
    import xml.etree.ElementTree as ET
    papers = []
    
    try:
        # Parse XML to a tree structure
        root = ET.fromstring(response)
        
        # Define namespaces used in arXiv XML
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
        }
        
        # Find all entries (papers)
        for entry in root.findall('.//atom:entry', namespaces):
            # First, check if the target author is in the authors list
            authors = []
            author_found = False
            
            for author in entry.findall('atom:author/atom:name', namespaces):
                if author.text is not None:
                    author_name = author.text.strip()
                    authors.append(author_name)
                    # Check if this author matches our target
                    if target_author and target_author.lower() in author_name.lower():
                        author_found = True
            
            # Only process this paper if the target author is found (or if no target specified)
            if target_author and not author_found:
                continue
            
            # Now extract all the paper details
            paper = {}
            paper['authors'] = authors
            
            # Get title
            title_elem = entry.find('atom:title', namespaces)
            if title_elem is not None and title_elem.text is not None:
                paper['title'] = title_elem.text.strip()
            
            # Get arXiv ID and links
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is not None and id_elem.text is not None:
                arxiv_id = id_elem.text.split('/')[-1]
                paper['links'] = {
                    'pdf': f"https://arxiv.org/pdf/{arxiv_id}",
                    'abstract': f"https://arxiv.org/abs/{arxiv_id}",
                    'arxiv_id': arxiv_id
                }
            
            # Get publication date
            published_elem = entry.find('atom:published', namespaces)
            if published_elem is not None:
                paper['publication_date'] = published_elem.text
            
            # Get categories
            categories = []
            for category in entry.findall('atom:category', namespaces):
                cat_term = category.get('term')
                if cat_term:
                    categories.append(cat_term)
            paper['categories'] = categories
            
            papers.append(paper)
        
        return papers
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    except Exception as e:
        print(f"Error processing arXiv response: {e}")
        return []
      
def get_papers_from_arxiv(name: str | None = None, school: str | None = None):
    # issue with people with the same name
    import urllib.parse
    import requests

    if not name:
        print("No author name provided")
        return []

    # Use more specific search terms
    # Try different search strategies to get better results
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
        print(f"Trying search: {search_query}")
        
        encoded_search_terms = urllib.parse.quote(search_query)
        url = f"http://export.arxiv.org/api/query?search_query={encoded_search_terms}&max_results=100"

        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the XML response (now with built-in author filtering)
            papers = parse_arxiv_response(response.text, name)
            
            # print(f"Found {len(papers)} papers for search '{search_query}'")
            all_papers.extend(papers)
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error for search '{search_query}': {e}")
            continue
    
    # Remove duplicates based on arXiv ID
    unique_papers = []
    seen_ids = set()
    for paper in all_papers:
        if 'links' in paper and 'arxiv_id' in paper['links']:
            arxiv_id = paper['links']['arxiv_id']
            if arxiv_id not in seen_ids:
                seen_ids.add(arxiv_id)
                unique_papers.append(paper)
    
    print(f"Total unique papers found: {len(unique_papers)}")
    return unique_papers

def parse_pubmed_response(response: str, target_author: str):
    # ================================
    # Example of papers
    # {
    #     "paper": {
    #         "title": "Paper Title",
    #         "authors": ["Author 1", "Author 2"],
    #         "links": {
    #             "pmid": "12345678",
    #             "abstract": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
    #             "pdf": None  # PubMed doesn't provide direct PDF links
    #         },
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
        
        # Find all articles
        for article in root.findall('.//PubmedArticle'):
            # Check if the target author/professor is in the authors list
            authors = []
            author_found = False
            
            for author in article.findall('.//Author'):
                last_name_elem = author.find('LastName')
                first_name_elem = author.find('ForeName')
                
                if last_name_elem is not None and last_name_elem.text:
                    last_name = last_name_elem.text.strip()
                    first_name = ""
                    if first_name_elem is not None and first_name_elem.text:
                        first_name = first_name_elem.text.strip()
                    
                    full_name = f"{first_name} {last_name}".strip()
                    if full_name:
                        authors.append(full_name)
                        # Check if this author matches our target professor
                        if target_author.lower() in full_name.lower():
                            author_found = True
            
            # Only process this paper if the professor is found
            if not author_found:
                continue
            
            # Now extract all the paper details
            paper = {}
            paper['authors'] = authors
            
            # Get PMID
            pmid_elem = article.find('.//PMID')
            if pmid_elem is not None and pmid_elem.text:
                pmid = pmid_elem.text
                paper['links'] = {
                    'pmid': pmid,
                    'abstract': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'pdf': None  # PubMed doesn't provide PDF links
                }
            
            # Get title
            title_elem = article.find('.//ArticleTitle')
            if title_elem is not None and title_elem.text:
                paper['title'] = title_elem.text.strip()
            
            # Get publication date
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
            
            # Get journal information
            journal_elem = article.find('.//Journal/Title')
            if journal_elem is not None and journal_elem.text:
                paper['journal'] = journal_elem.text.strip()
            
            # Get abstract
            abstract_elem = article.find('.//Abstract/AbstractText')
            if abstract_elem is not None and abstract_elem.text:
                paper['abstract'] = abstract_elem.text.strip()
            
            # Get MeSH terms (categories)
            categories = []
            for mesh_elem in article.findall('.//MeshHeadingList/MeshHeading/DescriptorName'):
                if mesh_elem.text:
                    categories.append(mesh_elem.text.strip())
            paper['categories'] = categories
            
            # Add the paper to our results
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
        print(f"PubMed search: {search_query}")
        
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
            
            print(f"Found {len(pmids)} papers for search: {search_query}")
            
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
    
    # Remove duplicates based on PMID
    unique_papers = []
    seen_pmids = set()
    for paper in all_papers:
        if 'links' in paper and 'pmid' in paper['links']:
            pmid = paper['links']['pmid']
            if pmid not in seen_pmids:
                seen_pmids.add(pmid)
                unique_papers.append(paper)
    
    print(f"Total unique PubMed papers found: {len(unique_papers)}")
    return unique_papers


def get_papers_from_google_scholar(name: str | None = None, school: str | None = None):
    pass

def get_papers_from_doaj(name: str | None = None, school: str | None = None):
    pass

def get_papers_from_semantic_scholar(name: str | None = None, school: str | None = None):
    pass

def get_papers_from_zenodo(name: str | None = None, school: str | None = None):
    pass

def get_papers_from_crossref(name: str | None = None, school: str | None = None):
    pass




# arXiv (have to include "Thank you to arXiv for use of its open access interoperability.")
# PubMed (NCBI API)
# Google Scholar (will be using scholarly, no official API)
# DOAJ (found)
# Semantic Scholar
# Zenodo 