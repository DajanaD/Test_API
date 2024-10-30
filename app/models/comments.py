from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description:  Mapped[str] = mapped_column(String(255), nullable=True)

    owner = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
