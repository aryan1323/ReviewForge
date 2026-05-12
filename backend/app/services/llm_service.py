import json
import logging
import time
from dataclasses import dataclass

from openai import AsyncAzureOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ReviewIssue:
    file_path: str
    line_number: int | None
    category: str
    severity: str
    message: str
    suggestion: str | None


@dataclass
class ReviewResult:
    summary: str
    overall_severity: str
    issues: list[ReviewIssue]
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int
    raw_response: str


_SYSTEM_PROMPT = """\
You are a senior software engineer performing a thorough code review.
Analyze the provided git diff and any relevant repository context.
Return ONLY a valid JSON object — no prose, no markdown fences, no explanation.
"""

_USER_TEMPLATE = """\
## Relevant Repository Context
{context}

## Pull Request Diff
{diff}

Review the diff for bugs, security vulnerabilities, performance issues, and style problems.
Use the repository context to understand existing patterns and conventions.

Respond with ONLY this JSON schema (no extra keys, no markdown):
{{
  "summary": "<2-3 sentence overall assessment>",
  "overall_severity": "low|medium|high|critical",
  "issues": [
    {{
      "file_path": "src/example.py",
      "line_number": 42,
      "category": "security|bug|performance|style|suggestion",
      "severity": "low|medium|high|critical",
      "message": "<what is wrong and why it matters>",
      "suggestion": "<how to fix it — include a code snippet if helpful, or null>"
    }}
  ]
}}
"""

_SEVERITY_WEIGHTS = {"critical": 4.0, "high": 2.0, "medium": 1.0, "low": 0.25}


class LLMService:
    def __init__(self) -> None:
        self._client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )

    async def review(self, diff_text: str, context_chunks: list[str]) -> ReviewResult:
        context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no relevant context retrieved)"
        user_msg = _USER_TEMPLATE.format(context=context, diff=diff_text)

        t0 = time.monotonic()
        response = await self._client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=1,  # o4-mini requires temperature=1
            response_format={"type": "json_object"},
        )
        latency_ms = int((time.monotonic() - t0) * 1000)

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)

        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        cost = (
            prompt_tokens * settings.OPENAI_INPUT_COST_PER_M / 1_000_000
            + completion_tokens * settings.OPENAI_OUTPUT_COST_PER_M / 1_000_000
        )

        issues = [
            ReviewIssue(
                file_path=i.get("file_path", "unknown"),
                line_number=i.get("line_number"),
                category=i.get("category", "suggestion"),
                severity=i.get("severity", "low"),
                message=i.get("message", ""),
                suggestion=i.get("suggestion"),
            )
            for i in data.get("issues", [])
        ]

        return ReviewResult(
            summary=data.get("summary", ""),
            overall_severity=data.get("overall_severity", "low"),
            issues=issues,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            raw_response=raw,
        )

    @staticmethod
    def compute_risk_score(issues: list[ReviewIssue]) -> float:
        if not issues:
            return 0.0
        total = sum(_SEVERITY_WEIGHTS.get(i.severity, 0.25) for i in issues)
        raw = total / len(issues)
        return round(min(raw * 2.5, 10.0), 2)  # scale to 0–10
