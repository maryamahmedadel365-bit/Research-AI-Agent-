"""
Database engine, session factory, and FastAPI dependency.

Supports **PostgreSQL** (when ``DATABASE_URL`` is set) and falls back to
**SQLite** automatically — so the app works on any machine with zero
external services.

Usage in a FastAPI route::

    from src.core.db import get_db

    @router.get("/example")
    def example(db: Session = Depends(get_db)):
        ...

Usage at startup (main.py lifespan)::

    from src.core.db import create_tables
    create_tables()           # safe to call repeatedly — only creates missing tables
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import get_settings


_settings = get_settings()
_url = _settings.effective_database_url

_connect_args: dict = {}
if not _settings.is_postgres:
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    _url,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    """Base class that every ORM model in the project must inherit from."""
    pass

def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and ensure it is closed after the request. """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables() -> None:
    """Create all tables that don't already exist."""
    Base.metadata.create_all(bind=engine)
