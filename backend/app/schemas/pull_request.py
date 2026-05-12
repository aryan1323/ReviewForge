import uuid
from datetime import datetime
from pydantic import BaseModel


class PRSummary(BaseModel):
    id: uuid.UUID
    repo_full_name: str
    number: int
    title: str
    author: str
    risk_score: float | None
    review_status: str
    overall_severity: str | None
    comment_count: int
    html_url: str
    opened_at: datetime
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}


class PRListResponse(BaseModel):
    items: list[PRSummary]
    total: int
    page: int
    page_size: int


class CommentOut(BaseModel):
    id: uuid.UUID
    file_path: str
    line_number: int | None
    category: str
    severity: str
    message: str
    suggestion: str | None

    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    id: uuid.UUID
    status: str
    model: str
    summary: str | None
    overall_severity: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_cost_usd: float | None
    latency_ms: int | None
    reviewed_at: datetime | None
    comments: list[CommentOut]

    model_config = {"from_attributes": True}


class PRDetailResponse(BaseModel):
    id: uuid.UUID
    repo_full_name: str
    number: int
    title: str
    author: str
    risk_score: float | None
    review_status: str
    html_url: str
    opened_at: datetime
    reviews: list[ReviewOut]

    model_config = {"from_attributes": True}
