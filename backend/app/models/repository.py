import uuid

from sqlalchemy import BigInteger, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)  # "owner/repo"
    installation_id: Mapped[int | None] = mapped_column(BigInteger)
    webhook_secret: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    pull_requests: Mapped[list["PullRequest"]] = relationship(back_populates="repository", cascade="all, delete-orphan")
    review_metrics: Mapped[list["ReviewMetric"]] = relationship(back_populates="repository")
    code_chunks: Mapped[list["CodeChunk"]] = relationship(back_populates="repository", cascade="all, delete-orphan")
