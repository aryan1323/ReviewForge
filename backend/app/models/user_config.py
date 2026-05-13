import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class UserConfig(Base, TimestampMixin):
    __tablename__ = "user_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    github_token: Mapped[str | None] = mapped_column(String)
    github_webhook_secret: Mapped[str | None] = mapped_column(String)
    azure_openai_api_key: Mapped[str | None] = mapped_column(String)
    azure_openai_endpoint: Mapped[str | None] = mapped_column(String)
    azure_deployment: Mapped[str | None] = mapped_column(String)
    azure_api_version: Mapped[str | None] = mapped_column(String)
    azure_embedding_deployment: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="config")
