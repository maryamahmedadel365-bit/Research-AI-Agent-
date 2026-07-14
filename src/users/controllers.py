from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from users import repository
from users.schemas import UserResponse, UserUpdatePushToken


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID."""
    user = repository.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}/push-token", response_model=UserResponse)
def update_push_token(
    user_id: int,
    body: UserUpdatePushToken,
    db: Session = Depends(get_db),
):
    """Register or update the Expo push token for a user's device."""
    user = repository.update_push_token(db, user_id, body.push_token)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
