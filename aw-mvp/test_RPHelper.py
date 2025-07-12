import RPHelper

def test_get_papers_from_arxiv():
    papers = RPHelper.get_papers_from_arxiv(name="Pingkun Yan")
    print(papers)

def test_get_papers_from_pubmed():
    papers = RPHelper.get_papers_from_pubmed(name="Pingkun Yan")
    print(papers)

def test_get_papers_from_google_scholar():
    papers = RPHelper.get_papers_from_google_scholar(name="Pingkun Yan")
    print(papers)

def test_get_papers_from_doaj():
    papers = RPHelper.get_papers_from_doaj(name="John Doe", school="University of California, Berkeley")
    print(papers)

def test_get_papers_from_semantic_scholar():
    papers = RPHelper.get_papers_from_semantic_scholar(name="John Doe", school="University of California, Berkeley")
    print(papers)

def test_get_papers_from_zenodo():
    papers = RPHelper.get_papers_from_zenodo(name="John Doe", school="University of California, Berkeley")
    print(papers)

def test_get_papers_from_crossref():
    papers = RPHelper.get_papers_from_crossref(name="John Doe", school="University of California, Berkeley")
    print(papers)

if __name__ == "__main__":
    # test_get_papers_from_arxiv() # issue with people with the same name
    test_get_papers_from_pubmed()
    # test_get_papers_from_google_scholar()
    # test_get_papers_from_doaj()
    # test_get_papers_from_semantic_scholar()
    # test_get_papers_from_zenodo()
    # test_get_papers_from_crossref()