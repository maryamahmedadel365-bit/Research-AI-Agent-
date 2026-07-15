"""arXiv paper fetching and analysis pipeline invocation.

Uses the arXiv Atom API (free, no key needed) to search for recent
AI/ML papers, picks one at random, downloads the PDF, and runs it
through the LangGraph analysis pipeline.
"""

import json
import os
import random
import tempfile
import urllib.request
from datetime import datetime
from urllib import parse

from .schemas import ArxivPaperMeta, PaperSummaryResponse

HF_DAILY_PAPERS_URL = "https://huggingface.co/api/daily_papers"


def _fetch_hf_daily_papers() -> list[ArxivPaperMeta]:
    """Fetch the top curated daily AI papers from HuggingFace."""
    req = urllib.request.Request(
        HF_DAILY_PAPERS_URL, 
        headers={"User-Agent": "Research-AI-Agent"}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read())

    papers: list[ArxivPaperMeta] = []
    
    for item in data:
        paper_data = item.get("paper", {})
        arxiv_id = paper_data.get("id")
        
        if not arxiv_id:
            continue
            
        title = paper_data.get("title", "").strip()
        abstract = paper_data.get("summary", "").strip()
        published_str = paper_data.get("publishedAt", "")
        
        authors = [
            author.get("name", "") 
            for author in paper_data.get("authors", [])
        ]
        
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        try:
            published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            published = datetime.now()
            
        papers.append(ArxivPaperMeta(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            authors=authors,
            pdf_url=pdf_url,
            published=published,
        ))

    return papers


def _download_pdf(pdf_url: str) -> str:
    """Download a PDF to a temp file and return the file path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        urllib.request.urlretrieve(pdf_url, tmp.name)
    except Exception:
        os.unlink(tmp.name)
        raise
    return tmp.name


def fetch_random_paper() -> ArxivPaperMeta:
    """Fetch recent AI papers from HuggingFace Daily Papers and pick one at random."""
    papers = _fetch_hf_daily_papers()
    if not papers:
        raise RuntimeError("No papers found from HuggingFace API")
    return random.choice(papers)

def fetch_paper_by_url(url: str) -> ArxivPaperMeta:
    """Extract arXiv ID from a URL and fetch its metadata from arXiv API."""
    import re
    import xml.etree.ElementTree as ET
    
    # Try to extract arXiv ID (e.g., from https://arxiv.org/abs/2310.12345 or https://arxiv.org/pdf/2310.12345.pdf)
    match = re.search(r'(\d{4}\.\d{4,5}(?:v\d+)?)', url)
    if not match:
        raise ValueError(f"Could not extract a valid arXiv ID from URL: {url}")
        
    arxiv_id = match.group(1)
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    req = urllib.request.Request(api_url, headers={"User-Agent": "Research-AI-Agent"})
    with urllib.request.urlopen(req, timeout=30) as response:
        xml_data = response.read()
        
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entry = root.find('atom:entry', ns)
    
    if entry is None:
        raise RuntimeError(f"Paper with ID {arxiv_id} not found on arXiv")
        
    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
    abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
    published_str = entry.find('atom:published', ns).text
    
    authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
    
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
    
    return ArxivPaperMeta(
        arxiv_id=arxiv_id,
        title=title,
        abstract=abstract,
        authors=authors,
        pdf_url=pdf_url,
        published=published,
    )


def analyze_paper(paper: ArxivPaperMeta) -> PaperSummaryResponse:
    """Download the paper's PDF, run the LangGraph analysis pipeline,
    and return the full summary response."""
    pdf_path = _download_pdf(paper.pdf_url)
    try:
        from ..analysis.graph import build_graph
        from ..analysis.state import initial_state

        graph = build_graph()
        result = graph.invoke(initial_state(pdf_path))

        if result.get("errors"):
            raise RuntimeError(f"Pipeline errors: {result['errors']}")

        paper_summary = result.get("paper_summary", {})

        return PaperSummaryResponse(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            abstract=paper.abstract,
            authors=paper.authors,
            pdf_url=paper.pdf_url,
            published=paper.published,
            methods=paper_summary.get("methods", ""),
            experiments=paper_summary.get("experiments", ""),
            limitations=paper_summary.get("limitations", ""),
            summary=paper_summary.get("summary", ""),
        )
    finally:
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


def get_random_paper_summary() -> PaperSummaryResponse:
    """End-to-end: pick a random paper → analyze → return summary."""
    paper = fetch_random_paper()
    summary = analyze_paper(paper)
    
    # Cache the result as the "Daily Paper"
    try:
        with open("daily_paper.json", "w") as f:
            f.write(summary.model_dump_json())
    except Exception as e:
        print(f"Failed to cache daily paper: {e}")
        
    return summary


def get_today_paper() -> PaperSummaryResponse:
    """Return the cached daily paper, or raise an error if not found."""
    if not os.path.exists("daily_paper.json"):
        raise RuntimeError("No daily paper has been processed yet today. The daily job must run first.")
    
    with open("daily_paper.json", "r") as f:
        data = json.load(f)
        return PaperSummaryResponse(**data)


def get_all_papers_from_notion() -> list[dict]:
    """Retrieve the last 50 papers stored in Notion."""
    import os
    from ..analysis.sinks.notion_sink import NotionPageWriter
    
    NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
    NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
    
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        raise RuntimeError("Notion configuration missing from environment variables")
        
    writer = NotionPageWriter(NOTION_TOKEN, NOTION_DATABASE_ID)
    papers = writer.get_all_papers()
    
    return [p.model_dump() for p in papers]
