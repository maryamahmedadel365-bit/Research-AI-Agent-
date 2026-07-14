from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from ..reading.models import ReadingLog


def log_paper_read(db: Session, user_id: int, arxiv_id: str) -> ReadingLog:
    """Log that a user has read a paper, ignoring duplicates."""
    # Check if already logged to avoid unique constraint failure
    existing = db.execute(
        select(ReadingLog).where(
            ReadingLog.user_id == user_id, 
            ReadingLog.arxiv_id == arxiv_id
        )
    ).scalar_one_or_none()
    
    if existing:
        return existing
        
    new_log = ReadingLog(user_id=user_id, arxiv_id=arxiv_id)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


def get_user_streak(db: Session, user_id: int) -> dict:
    """Calculate the user's current reading streak and longest streak in days."""
    logs = db.execute(
        select(ReadingLog.read_at)
        .where(ReadingLog.user_id == user_id)
        .order_by(desc(ReadingLog.read_at))
    ).scalars().all()
    
    if not logs:
        return {"current_streak": 0, "longest_streak": 0, "last_read_at": None}
        
    # Extract unique dates the user read a paper (ignoring time)
    read_dates = sorted(list({log.date() for log in logs}), reverse=True)
    
    current_streak = 0
    longest_streak = 0
    current_run = 0
    
    today = date.today()
    
    # Calculate current streak
    # The streak continues if they read today OR yesterday
    if read_dates and (today - read_dates[0]).days <= 1:
        current_streak = 1
        for i in range(1, len(read_dates)):
            if (read_dates[i-1] - read_dates[i]).days == 1:
                current_streak += 1
            else:
                break
                
    # Calculate longest streak historically
    if read_dates:
        current_run = 1
        longest_streak = 1
        for i in range(1, len(read_dates)):
            if (read_dates[i-1] - read_dates[i]).days == 1:
                current_run += 1
                longest_streak = max(longest_streak, current_run)
            else:
                current_run = 1
                
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_read_at": logs[0]
    }
