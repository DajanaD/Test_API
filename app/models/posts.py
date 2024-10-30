from sqlalchemy import Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    comments_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="posts", lazy="joined")
    owner = relationship("User")
    comment = relationship("Comment", back_populates="posts")
