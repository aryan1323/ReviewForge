from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    weeks: int = Query(12, ge=1, le=52, description="Number of past weeks to aggregate"),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    return await ReviewService(db).get_analytics(weeks=weeks)
