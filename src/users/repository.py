from sqlalchemy.orm import Session

from .models import User

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_name(db: Session, name: str) -> User | None:
    return db.query(User).filter(User.name == name).first()


def update_push_token(db: Session, user_id: int, push_token: str) -> User | None:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    user.push_token = push_token
    db.commit()
    db.refresh(user)
    return user


def seed_users(db: Session) -> None:
    """Create the two hardcoded users if they don't exist yet."""
    default_users = ["Aly", "Maryam"]

    for name in default_users:
        existing = get_user_by_name(db, name)
        if existing is None:
            db.add(User(name=name))

    db.commit()
