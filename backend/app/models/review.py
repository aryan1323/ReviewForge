import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pull_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False)
    rq_job_id: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str] = mapped_column(Text, default="gpt-4o", nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    total_cost_usd: Mapped[float | None] = mapped_column(Numeric(10, 6))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    raw_llm_response: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    # low | medium | high | critical
    overall_severity: Mapped[str | None] = mapped_column(Text)
    # pending | running | completed | failed
    status: Mapped[str] = mapped_column(Text, default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    pull_request: Mapped["PullRequest"] = relationship(back_populates="reviews")
    comments: Mapped[list["ReviewComment"]] = relationship(back_populates="review", cascade="all, delete-orphan")
    metrics: Mapped["ReviewMetric | None"] = relationship(back_populates="review", uselist=False)
