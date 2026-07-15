from fastapi import APIRouter, HTTPException, Depends
import os

from .schemas import ArxivPaperMeta, PaperSummaryResponse
from . import services
from ..notifications.services import send_daily_reminder_to_all


router = APIRouter(prefix="/api/papers", tags=["Papers"])


def verify_cron_secret(secret: str = ""):
    expected = os.getenv("CRON_SECRET", "super-secret-daily-job")
    if secret != expected:
        raise HTTPException(status_code=403, detail="Invalid cron secret")


@router.get("/today", response_model=PaperSummaryResponse)
def get_today_paper():
    """Fetch the cached daily paper that was saved to Notion today."""
    try:
        paper = services.get_today_paper()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return paper


@router.get("/all", response_model=list[PaperSummaryResponse])
def get_all_papers():
    """Fetch all papers stored in Notion (limit 50)."""
    try:
        papers = services.get_all_papers_from_notion()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return papers

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


from pydantic import BaseModel

class UrlRequest(BaseModel):
    url: str

@router.post("/analyze-url", response_model=PaperSummaryResponse)
def analyze_paper_by_url(req: UrlRequest):
    """Analyze a specific paper from an arXiv URL."""
    try:
        paper_meta = services.fetch_paper_by_url(req.url)
        result = services.analyze_paper(paper_meta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    return result


@router.post("/daily-job", dependencies=[Depends(verify_cron_secret)])
def run_daily_job():
    """Triggered by GitHub Actions to run the full daily process."""
    try:
        # 1. Fetch random paper, run LangGraph, save to Notion
        result = services.get_random_paper_summary()
        # 2. Send push notifications
        send_daily_reminder_to_all()
        return {"status": "success", "message": "Daily job completed.", "paper": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily job failed: {e}")

