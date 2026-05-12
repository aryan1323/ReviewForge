import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class ReviewMetric(Base, TimestampMixin):
    __tablename__ = "review_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    bug_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    security_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    style_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    performance_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_comments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)

    review: Mapped["Review"] = relationship(back_populates="metrics")
    repository: Mapped["Repository"] = relationship(back_populates="review_metrics")
