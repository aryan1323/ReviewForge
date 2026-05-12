import pytest
from unittest.mock import AsyncMock, patch

from app.services.llm_service import LLMService, ReviewIssue


@pytest.mark.asyncio
async def test_review_returns_structured_result(sample_diff, mock_openai_response):
    with patch("app.services.llm_service.AsyncOpenAI") as mock_cls:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
        mock_cls.return_value = mock_client

        svc = LLMService()
        result = await svc.review(sample_diff, context_chunks=[])

    assert result.overall_severity == "critical"
    assert len(result.issues) == 1
    assert result.issues[0].category == "security"
    assert result.issues[0].file_path == "src/auth.py"
    assert result.prompt_tokens == 500
    assert result.completion_tokens == 150
    assert result.cost_usd > 0


def test_compute_risk_score_empty():
    assert LLMService.compute_risk_score([]) == 0.0


def test_compute_risk_score_critical():
    issues = [
        ReviewIssue("f", 1, "security", "critical", "msg", None),
        ReviewIssue("f", 2, "bug", "high", "msg", None),
    ]
    score = LLMService.compute_risk_score(issues)
    assert 0.0 < score <= 10.0


def test_compute_risk_score_low_issues():
    issues = [ReviewIssue("f", i, "style", "low", "msg", None) for i in range(5)]
    score = LLMService.compute_risk_score(issues)
    assert score < 2.0
