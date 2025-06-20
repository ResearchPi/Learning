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
    '''
    '''
    print(f"Name: {query['name']}")
    print(f"School: {query['school']}")

def test_print_papers(papers: list[str]):
    '''
    '''
    for i,paper in enumerate(papers):
        print(f"Paper {i+1}: {paper}")
        print("-"*100)

def get_papers_topics(query: dict):
    '''
    '''
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

def get_papers_from_arxiv(name: str = None, school: str = None):
    '''
    '''

    pass


def get_papers_from_pubmed(name: str = None, school: str = None):
    '''
    '''

    pass


def get_papers_from_google_scholar(name: str = None, school: str = None):
    '''
    Google Scholar API is not available, so we will be using the scholarly library
    '''
    pass


def get_papers_from_doaj(name: str = None, school: str = None):
    '''
    '''
    pass


def get_papers_from_semantic_scholar(name: str = None, school: str = None):
    '''
    '''
    pass

def get_papers_from_zenodo(name: str = None, school: str = None):
    '''
    '''
    pass

def get_papers_from_crossref(name: str = None, school: str = None):
    '''
    '''
    pass




# arXiv (have to include "Thank you to arXiv for use of its open access interoperability.")
# PubMed (NCBI API)
# Google Scholar (will be using scholarly, no official API)
# DOAJ (found)
# Semantic Scholar
# Zenodo 