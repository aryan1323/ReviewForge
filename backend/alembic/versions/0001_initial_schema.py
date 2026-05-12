"""initial schema"""
from typing import Sequence
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "repositories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("github_id", sa.BigInteger, unique=True, nullable=False),
        sa.Column("full_name", sa.Text, nullable=False),
        sa.Column("installation_id", sa.BigInteger),
        sa.Column("webhook_secret", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "pull_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("github_pr_id", sa.BigInteger, nullable=False),
        sa.Column("number", sa.Integer, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("author", sa.Text, nullable=False),
        sa.Column("base_branch", sa.Text, nullable=False),
        sa.Column("head_branch", sa.Text, nullable=False),
        sa.Column("head_sha", sa.Text, nullable=False),
        sa.Column("diff_url", sa.Text, nullable=False),
        sa.Column("html_url", sa.Text, nullable=False),
        sa.Column("state", sa.Text, default="open", nullable=False),
        sa.Column("risk_score", sa.Numeric(4, 2)),
        sa.Column("review_status", sa.Text, default="pending", nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("repository_id", "github_pr_id"),
    )
    op.create_index("idx_prs_repo_id", "pull_requests", ["repository_id"])
    op.create_index("idx_prs_review_status", "pull_requests", ["review_status"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pull_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rq_job_id", sa.Text),
        sa.Column("model", sa.Text, default="gpt-4o", nullable=False),
        sa.Column("prompt_tokens", sa.Integer),
        sa.Column("completion_tokens", sa.Integer),
        sa.Column("total_cost_usd", sa.Numeric(10, 6)),
        sa.Column("latency_ms", sa.Integer),
        sa.Column("raw_llm_response", sa.Text),
        sa.Column("summary", sa.Text),
        sa.Column("overall_severity", sa.Text),
        sa.Column("status", sa.Text, default="pending", nullable=False),
        sa.Column("error_message", sa.Text),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_reviews_pr_id", "reviews", ["pull_request_id"])

    op.create_table(
        "review_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("review_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("github_comment_id", sa.BigInteger),
        sa.Column("file_path", sa.Text, nullable=False),
        sa.Column("line_number", sa.Integer),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("severity", sa.Text, nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("suggestion", sa.Text),
        sa.Column("position", sa.Integer),
        sa.Column("posted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_comments_review", "review_comments", ["review_id"])

    op.create_table(
        "review_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("review_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("week_start", sa.Date, nullable=False),
        sa.Column("bug_count", sa.Integer, default=0, nullable=False),
        sa.Column("security_count", sa.Integer, default=0, nullable=False),
        sa.Column("style_count", sa.Integer, default=0, nullable=False),
        sa.Column("performance_count", sa.Integer, default=0, nullable=False),
        sa.Column("total_comments", sa.Integer, default=0, nullable=False),
        sa.Column("prompt_tokens", sa.Integer, default=0, nullable=False),
        sa.Column("completion_tokens", sa.Integer, default=0, nullable=False),
        sa.Column("cost_usd", sa.Numeric(10, 6), default=0, nullable=False),
        sa.Column("latency_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_metrics_week", "review_metrics", ["week_start", "repository_id"])

    # pgvector table for RAG
    op.execute("""
        CREATE TABLE code_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
            file_path TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536) NOT NULL,
            indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (repository_id, file_path, chunk_index)
        )
    """)
    op.execute("""
        CREATE INDEX idx_code_chunks_embedding
        ON code_chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    op.drop_table("code_chunks")
    op.drop_table("review_metrics")
    op.drop_table("review_comments")
    op.drop_table("reviews")
    op.drop_table("pull_requests")
    op.drop_table("repositories")
