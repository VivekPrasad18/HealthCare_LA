import os
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "your_email@example.com")
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_pubmed(query: str, max_results: int = 5) -> List[str]:
    """Search PubMed and return a list of PMIDs."""
    url = f"{BASE_URL}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "email": PUBMED_EMAIL
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_paper_details(pmids: List[str]) -> List[Dict[str, Any]]:
    """Fetch metadata and abstract for a list of PMIDs."""
    if not pmids:
        return []
    
    url = f"{BASE_URL}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": PUBMED_EMAIL
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Parse the XML response
    root = ET.fromstring(response.content)
    papers = []
    
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        
        # Combine abstract sections (some abstracts are split by Background, Methods, etc.)
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join([t.text for t in abstract_texts if t.text]) if abstract_texts else None
        
        year = article.findtext(".//PubDate/Year") or article.findtext(".//ArticleDate/Year")
        
        doi = None
        for el in article.findall(".//ArticleId"):
            if el.attrib.get("IdType") == "doi":
                doi = el.text
                break
                
        authors = []
        for author in article.findall(".//Author"):
            last_name = author.findtext("LastName")
            initials = author.findtext("Initials")
            if last_name:
                name = f"{last_name} {initials}" if initials else last_name
                authors.append(name)
                
        paper = {
            "pmid": pmid,
            "doi": doi,
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
        }
        papers.append(paper)
        
    return papers

def query_pubmed(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Complete pipeline to search and fetch papers."""
    pmids = search_pubmed(query, max_results)
    return fetch_paper_details(pmids)

if __name__ == "__main__":
    # Quick local test
    print("Searching PubMed for: 'diabetic retinopathy deep learning'...")
    results = query_pubmed("diabetic retinopathy deep learning", max_results=2)
    for res in results:
        print(f"\nTitle: {res['title']}")
        print(f"Authors: {', '.join(res['authors'])}")
        print(f"Year: {res['year']}")
        print(f"URL: {res['url']}")
        print(f"Abstract Snippet: {str(res['abstract'])[:150]}...")