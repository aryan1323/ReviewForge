import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class PullRequest(Base, TimestampMixin):
    __tablename__ = "pull_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    github_pr_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    base_branch: Mapped[str] = mapped_column(Text, nullable=False)
    head_branch: Mapped[str] = mapped_column(Text, nullable=False)
    head_sha: Mapped[str] = mapped_column(Text, nullable=False)
    diff_url: Mapped[str] = mapped_column(Text, nullable=False)
    html_url: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(Text, default="open", nullable=False)
    risk_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    # pending | reviewing | completed | failed
    review_status: Mapped[str] = mapped_column(Text, default="pending", nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    repository: Mapped["Repository"] = relationship(back_populates="pull_requests")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="pull_request",
        cascade="all, delete-orphan",
        order_by="Review.created_at.desc()",
    )
