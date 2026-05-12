import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import PullRequest, Repository
from app.schemas.webhook import GitHubWebhookPayload

logger = logging.getLogger(__name__)
settings = get_settings()

_HANDLED_ACTIONS = {"opened", "synchronize", "reopened"}


class WebhookService:
    async def handle(
        self,
        event: str,
        signature: str,
        body: bytes,
        db: AsyncSession,
    ) -> None:
        logger.info("Received GitHub event: %s", event)
        if event != "pull_request":
            logger.info("Ignoring non-PR event: %s", event)
            return

        payload_data = json.loads(body)
        action = payload_data.get("action", "")
        logger.info("PR action: %s", action)
        if action not in _HANDLED_ACTIONS:
            logger.info("Ignoring PR action: %s", action)
            return

        # Verify HMAC signature before any DB writes
        self._verify_signature(body, signature, settings.GITHUB_WEBHOOK_SECRET)

        payload = GitHubWebhookPayload(**payload_data)
        repo = await self._get_or_create_repo(payload, db)

        pr = await self._upsert_pull_request(payload, repo, db)
        await db.commit()

        # Enqueue rq job (import here to avoid circular imports at module load)
        from app.tasks.queue import review_queue
        from app.tasks.review_tasks import review_pr

        job = review_queue.enqueue(
            review_pr,
            kwargs={
                "pr_id": str(pr.id),
                "repo_full_name": repo.full_name,
                "pr_number": pr.number,
            },
            retry=3,
        )
        logger.info("Enqueued review job %s for PR #%s", job.id, pr.number)

    @staticmethod
    def _verify_signature(body: bytes, signature: str, secret: str) -> None:
        expected = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    async def _get_or_create_repo(
        self, payload: GitHubWebhookPayload, db: AsyncSession
    ) -> Repository:
        result = await db.execute(
            select(Repository).where(Repository.github_id == payload.repository.id)
        )
        repo = result.scalar_one_or_none()
        if repo is None:
            repo = Repository(
                github_id=payload.repository.id,
                full_name=payload.repository.full_name,
                webhook_secret=settings.GITHUB_WEBHOOK_SECRET,
            )
            db.add(repo)
            await db.flush()
            logger.info("Registered new repository: %s", repo.full_name)
        return repo

    async def _upsert_pull_request(
        self, payload: GitHubWebhookPayload, repo: Repository, db: AsyncSession
    ) -> PullRequest:
        gh_pr = payload.pull_request
        result = await db.execute(
            select(PullRequest).where(
                PullRequest.repository_id == repo.id,
                PullRequest.github_pr_id == gh_pr.id,
            )
        )
        pr = result.scalar_one_or_none()

        opened_at = datetime.fromisoformat(gh_pr.created_at.replace("Z", "+00:00"))

        if pr is None:
            pr = PullRequest(
                repository_id=repo.id,
                github_pr_id=gh_pr.id,
                number=gh_pr.number,
                title=gh_pr.title,
                author=gh_pr.user.login,
                base_branch=gh_pr.base.ref,
                head_branch=gh_pr.head.ref,
                head_sha=gh_pr.head.sha,
                diff_url=gh_pr.diff_url,
                html_url=gh_pr.html_url,
                state=gh_pr.state,
                review_status="pending",
                opened_at=opened_at,
            )
            db.add(pr)
        else:
            pr.head_sha = gh_pr.head.sha
            pr.review_status = "pending"
            pr.state = gh_pr.state

        await db.flush()
        return pr
