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

def get_papers_topics(query: dict):
    # ================================
    # Parse Query
    # ================================
    name: str = query.get('name', None)
    school: str = query.get('school', None)
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
    papers.extend(get_papers_from_pubmed(name, school))
    papers.extend(get_papers_from_google_scholar(name, school))
    papers.extend(get_papers_from_doaj(name, school))
    papers.extend(get_papers_from_semantic_scholar(name, school))
    papers.extend(get_papers_from_zenodo(name, school))
    papers.extend(get_papers_from_crossref(name, school))
    test_print_papers(papers)
    pass

    # ================================
    # Get Keywords/Topics
    # ================================
    pass

def parse_arxiv_response(response: str):
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
            paper = {}
            
            # Get title
            title_elem = entry.find('atom:title', namespaces)
            if title_elem is not None:
                paper['title'] = title_elem.text.strip()
            
            # Get authors
            authors = []
            for author in entry.findall('atom:author/atom:name', namespaces):
                authors.append(author.text.strip())
            paper['authors'] = authors
            
            # Get arXiv ID and links
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is not None:
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

def get_papers_from_arxiv(name: str = None, school: str = None):
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
            
            # Parse the XML response
            papers = parse_arxiv_response(response.text)
            
            # Filter papers to ensure the author is actually in the authors list
            filtered_papers = []
            for paper in papers:
                if 'authors' in paper and paper['authors']:
                    # Check if the target author is in the authors list
                    # Use case-insensitive partial matching
                    author_found = False
                    for author in paper['authors']:
                        if name.lower() in author.lower():
                            author_found = True
                            break
                    
                    if author_found:
                        filtered_papers.append(paper)
                        # print(f"Found paper: {paper.get('title', 'No title')} by {paper.get('authors', [])}")
            
            # print(f"Found {len(filtered_papers)} papers for search '{search_query}'")
            all_papers.extend(filtered_papers)
            
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

def get_papers_from_pubmed(name: str = None, school: str = None):
    pass


def get_papers_from_google_scholar(name: str = None, school: str = None):
    pass


def get_papers_from_doaj(name: str = None, school: str = None):
    pass


def get_papers_from_semantic_scholar(name: str = None, school: str = None):
    pass

def get_papers_from_zenodo(name: str = None, school: str = None):
    pass

def get_papers_from_crossref(name: str = None, school: str = None):
    pass




# arXiv (have to include "Thank you to arXiv for use of its open access interoperability.")
# PubMed (NCBI API)
# Google Scholar (will be using scholarly, no official API)
# DOAJ (found)
# Semantic Scholar
# Zenodo 