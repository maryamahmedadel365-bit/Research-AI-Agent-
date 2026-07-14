from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db import Base


class ReadingLog(Base):
    """Records that a specific user read a specific paper."""
    __tablename__ = "reading_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    arxiv_id: Mapped[str] = mapped_column(String(100), nullable=False)
    read_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Prevent duplicate logging of the same paper on the same day if necessary
    # (Optional, but good for data integrity)
    __table_args__ = (
        UniqueConstraint("user_id", "arxiv_id", name="uix_user_arxiv"),
    )
