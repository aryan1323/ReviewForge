import logging
from datetime import datetime, timezone

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_GITHUB_API = "https://api.github.com"


class GitHubService:
    def __init__(self, token: str | None = None) -> None:
        self._token = token or settings.GITHUB_TOKEN
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """Fetch raw unified diff for a pull request."""
        url = f"{_GITHUB_API}/repos/{repo}/pulls/{pr_number}"
        headers = {**self._headers, "Accept": "application/vnd.github.v3.diff"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text

    async def get_repo_info(self, repo: str) -> dict:
        url = f"{_GITHUB_API}/repos/{repo}"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def post_review_comments(
        self,
        repo: str,
        pr_number: int,
        head_sha: str,
        comments: list[dict],
        summary: str = "",
    ) -> list[int]:
        """
        Post all review comments in a single GitHub review submission.
        Returns list of github_comment_ids (one per comment in the response).
        """
        url = f"{_GITHUB_API}/repos/{repo}/pulls/{pr_number}/reviews"

        # Filter out comments with no valid position (GitHub rejects them)
        valid_comments = [
            {
                "path": c["file_path"],
                "line": c["line_number"],
                "body": self._format_comment_body(c),
            }
            for c in comments
            if c.get("line_number")
        ]

        payload = {
            "commit_id": head_sha,
            "body": summary or "Automated code review by PR Bot.",
            "event": "COMMENT",
            "comments": valid_comments,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=self._headers, json=payload)
            if resp.status_code == 422:
                logger.warning("GitHub rejected review (422): %s", resp.text)
                return []
            resp.raise_for_status()
            data = resp.json()

        return [c.get("id", 0) for c in data.get("comments", [])]

    @staticmethod
    def _format_comment_body(comment: dict) -> str:
        severity_emoji = {"low": "ℹ️", "medium": "⚠️", "high": "🔴", "critical": "🚨"}
        emoji = severity_emoji.get(comment["severity"], "ℹ️")
        body = f"{emoji} **[{comment['category'].upper()} / {comment['severity'].upper()}]** {comment['message']}"
        if comment.get("suggestion"):
            body += f"\n\n**Suggestion:**\n```\n{comment['suggestion']}\n```"
        return body
