from pydantic import BaseModel


class WeeklyBugTrend(BaseModel):
    week_start: str
    bug_count: int
    security_count: int
    style_count: int
    performance_count: int


class WeeklyCost(BaseModel):
    week_start: str
    cost_usd: float
    prompt_tokens: int
    completion_tokens: int


class LatencyBucket(BaseModel):
    label: str
    count: int


class SeverityBreakdown(BaseModel):
    low: int
    medium: int
    high: int
    critical: int


class AnalyticsResponse(BaseModel):
    total_prs_reviewed: int
    avg_risk_score: float | None
    avg_latency_ms: float | None
    total_cost_usd: float
    severity_breakdown: SeverityBreakdown
    weekly_bug_trend: list[WeeklyBugTrend]
    weekly_cost: list[WeeklyCost]
    latency_buckets: list[LatencyBucket]
