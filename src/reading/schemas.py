from datetime import datetime
from pydantic import BaseModel


class ReadingLogCreate(BaseModel):
    user_id: int
    arxiv_id: str


class ReadingLogResponse(BaseModel):
    id: int
    user_id: int
    arxiv_id: str
    read_at: datetime

    model_config = {"from_attributes": True}


class StreakResponse(BaseModel):
    user_id: int
    current_streak: int
    longest_streak: int
    last_read_at: datetime | None
