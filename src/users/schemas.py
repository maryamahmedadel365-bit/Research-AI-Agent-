from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    push_token: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdatePushToken(BaseModel):
    push_token: str
