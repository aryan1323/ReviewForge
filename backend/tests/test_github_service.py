import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.github_service import GitHubService


@pytest.mark.asyncio
async def test_get_pr_diff_returns_text():
    fake_diff = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new"

    with patch("app.services.github_service.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = fake_diff
        mock_response.raise_for_status = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        svc = GitHubService(token="fake-token")
        diff = await svc.get_pr_diff("owner/repo", 42)

    assert diff == fake_diff


def test_format_comment_body_with_suggestion():
    comment = {
        "file_path": "src/auth.py",
        "line_number": 10,
        "category": "security",
        "severity": "critical",
        "message": "SQL injection",
        "suggestion": "Use parameterized queries",
    }
    body = GitHubService._format_comment_body(comment)
    assert "SQL injection" in body
    assert "CRITICAL" in body
    assert "Use parameterized queries" in body
    assert "🚨" in body


def test_format_comment_body_no_suggestion():
    comment = {
        "file_path": "f",
        "line_number": 1,
        "category": "style",
        "severity": "low",
        "message": "Missing newline",
        "suggestion": None,
    }
    body = GitHubService._format_comment_body(comment)
    assert "Missing newline" in body
    assert "Suggestion" not in body
