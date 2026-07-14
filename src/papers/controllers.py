from fastapi import APIRouter, HTTPException

from .schemas import ArxivPaperMeta, PaperSummaryResponse
from . import services


router = APIRouter(prefix="/api/papers", tags=["Papers"])


@router.get("/random", response_model=ArxivPaperMeta)
def get_random_paper():
    """Fetch a random recent AI paper from arXiv (metadata only, no analysis)."""
    try:
        paper = services.fetch_random_paper()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"arXiv fetch failed: {e}")
    return paper


@router.post("/analyze", response_model=PaperSummaryResponse)
def analyze_random_paper():
    """Pick a random paper, run the full LangGraph analysis pipeline, and return the summary."""
    try:
        result = services.get_random_paper_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    return result


@router.post("/analyze-url", response_model=PaperSummaryResponse)
def analyze_paper_by_url(paper: ArxivPaperMeta):
    """Analyze a specific paper (pass its full ArxivPaperMeta as the body)."""
    try:
        result = services.analyze_paper(paper)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    return result
