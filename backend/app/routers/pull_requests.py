import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.pull_request import PRDetailResponse, PRListResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/prs", tags=["pull_requests"])


@router.get("", response_model=PRListResponse)
async def list_prs(
    repo: str | None = Query(None, description="Filter by repo full_name (owner/repo)"),
    status: str | None = Query(None, description="Filter by review_status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PRListResponse:
    return await ReviewService(db).list_prs(repo=repo, status=status, page=page, page_size=page_size)


@router.get("/{pr_id}", response_model=PRDetailResponse)
async def get_pr(
    pr_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PRDetailResponse:
    detail = await ReviewService(db).get_pr_detail(pr_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="PR not found")
    return detail
