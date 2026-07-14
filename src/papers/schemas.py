from datetime import datetime

from pydantic import BaseModel


class ArxivPaperMeta(BaseModel):
    """Metadata about a paper fetched from arXiv (before analysis)."""
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    pdf_url: str
    published: datetime


class PaperSummaryResponse(BaseModel):
    """Full response after the analysis pipeline runs."""
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    pdf_url: str
    published: datetime
    methods: str
    experiments: str
    limitations: str
    summary: str
