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
    return analyze_paper(paper)
