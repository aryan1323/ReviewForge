"""
rq job: review_pr

Runs synchronously inside the rq worker process (not async).
Uses asyncio.run() to call async services.
"""
import asyncio
import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.metrics.prometheus import (
    cost_usd_total,
    issues_found_total,
    review_latency_ms,
    reviews_total,
    tokens_used_total,
)
from app.models import PullRequest, Repository, Review, ReviewComment, ReviewMetric
from app.models.user_config import UserConfig
from app.rag.indexer import index_repository
from app.rag.retriever import get_relevant_context
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)
settings = get_settings()


def review_pr(pr_id: str, repo_full_name: str, pr_number: int) -> None:
    """Entry point called by rq worker."""
    asyncio.run(_review_pr_async(pr_id, repo_full_name, pr_number))


async def _review_pr_async(pr_id: str, repo_full_name: str, pr_number: int) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    _engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    _session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with _session() as db:
            result = await db.execute(
                select(PullRequest)
                .where(PullRequest.id == pr_id)
                .options(selectinload(PullRequest.repository))
            )
            pr = result.scalar_one()
            repo: Repository = pr.repository

            review = Review(pull_request_id=pr.id, status="running")
            db.add(review)
            pr.review_status = "reviewing"
            await db.commit()
            await db.refresh(review)

            user_config = None
            if repo.user_id:
                cfg_result = await db.execute(select(UserConfig).where(UserConfig.user_id == repo.user_id))
                user_config = cfg_result.scalar_one_or_none()

            github_token = (user_config and user_config.github_token) or settings.GITHUB_TOKEN
            github = GitHubService(token=github_token)
            llm = LLMService(user_config=user_config)

            try:
                await _ensure_indexed(db, repo)
                diff_text = await github.get_pr_diff(repo_full_name, pr_number)
                context_chunks = await get_relevant_context(db, repo.id, diff_text)
                logger.info("Retrieved %d context chunks for PR #%s", len(context_chunks), pr_number)

                result_data = await llm.review(diff_text, context_chunks)

                review.summary = result_data.summary
                review.overall_severity = result_data.overall_severity
                review.prompt_tokens = result_data.prompt_tokens
                review.completion_tokens = result_data.completion_tokens
                review.total_cost_usd = result_data.cost_usd
                review.latency_ms = result_data.latency_ms
                review.raw_llm_response = result_data.raw_response
                review.status = "completed"
                review.reviewed_at = datetime.now(timezone.utc)

                for issue in result_data.issues:
                    db.add(ReviewComment(
                        review_id=review.id,
                        file_path=issue.file_path,
                        line_number=issue.line_number,
                        category=issue.category,
                        severity=issue.severity,
                        message=issue.message,
                        suggestion=issue.suggestion,
                    ))

                risk_score = llm.compute_risk_score(result_data.issues)
                pr.risk_score = risk_score
                pr.review_status = "completed"
                await db.flush()

                today = date.today()
                week_start = today - timedelta(days=today.weekday())
                counts = _count_by_category(result_data.issues)
                db.add(ReviewMetric(
                    review_id=review.id,
                    repository_id=repo.id,
                    week_start=week_start,
                    bug_count=counts["bug"],
                    security_count=counts["security"],
                    style_count=counts["style"],
                    performance_count=counts["performance"],
                    total_comments=len(result_data.issues),
                    prompt_tokens=result_data.prompt_tokens,
                    completion_tokens=result_data.completion_tokens,
                    cost_usd=result_data.cost_usd,
                    latency_ms=result_data.latency_ms,
                ))
                await db.commit()

                reviews_total.labels(status="completed").inc()
                review_latency_ms.observe(result_data.latency_ms)
                tokens_used_total.labels(type="input").inc(result_data.prompt_tokens)
                tokens_used_total.labels(type="output").inc(result_data.completion_tokens)
                cost_usd_total.inc(result_data.cost_usd)
                for issue in result_data.issues:
                    issues_found_total.labels(category=issue.category, severity=issue.severity).inc()

                logger.info(
                    "Completed review for PR #%s: risk=%.2f, issues=%d, cost=$%.4f",
                    pr_number, risk_score, len(result_data.issues), result_data.cost_usd,
                )

            except Exception as exc:
                logger.exception("Review failed for PR #%s: %s", pr_number, exc)
                review.status = "failed"
                review.error_message = str(exc)
                pr.review_status = "failed"
                await db.commit()
                reviews_total.labels(status="failed").inc()
                raise
    finally:
        await _engine.dispose()


async def _ensure_indexed(db, repo: Repository) -> None:
    """Index the repo into pgvector if it hasn't been indexed yet."""
    from sqlalchemy import text
    result = await db.execute(
        text("SELECT COUNT(*) FROM code_chunks WHERE repository_id = :id"),
        {"id": str(repo.id)},
    )
    if result.scalar_one() == 0:
        logger.info("No chunks found for %s — indexing now", repo.full_name)
        count = await index_repository(db, repo.id, repo.full_name, settings.GITHUB_TOKEN)
        logger.info("Indexed %d chunks for %s", count, repo.full_name)


def _count_by_category(issues) -> dict[str, int]:
    counts: dict[str, int] = {"bug": 0, "security": 0, "style": 0, "performance": 0, "suggestion": 0}
    for issue in issues:
        cat = issue.category if issue.category in counts else "suggestion"
        counts[cat] += 1
    return counts
