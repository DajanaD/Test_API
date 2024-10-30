from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from enum import Enum as PyEnum
import datetime

class CommentStatus(PyEnum):
    CREATED = "created"
    BLOCKED = "blocked"

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    status: Mapped[CommentStatus] = mapped_column(Enum(CommentStatus), default=CommentStatus.CREATED)

    owner = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
