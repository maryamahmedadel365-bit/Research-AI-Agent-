from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..reading import repository
from ..reading.schemas import ReadingLogCreate, ReadingLogResponse, StreakResponse
from ..users.repository import get_user_by_id

router = APIRouter(prefix="/api/reading", tags=["Reading"])


@router.post("/log", response_model=ReadingLogResponse)
def log_reading(body: ReadingLogCreate, db: Session = Depends(get_db)):
    """Log that a user read a paper to keep their streak going."""
    user = get_user_by_id(db, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return repository.log_paper_read(db, body.user_id, body.arxiv_id)


@router.get("/streak/{user_id}", response_model=StreakResponse)
def get_streak(user_id: int, db: Session = Depends(get_db)):
    """Get the current reading streak for a specific user."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    streak_data = repository.get_user_streak(db, user_id)
    return StreakResponse(
        user_id=user_id,
        current_streak=streak_data["current_streak"],
        longest_streak=streak_data["longest_streak"],
        last_read_at=streak_data["last_read_at"],
    )
