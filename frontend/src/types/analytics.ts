export interface WeeklyBugTrend {
  week_start: string
  bug_count: number
  security_count: number
  style_count: number
  performance_count: number
}

export interface WeeklyCost {
  week_start: string
  cost_usd: number
  prompt_tokens: number
  completion_tokens: number
}

export interface LatencyBucket {
  label: string
  count: number
}

export interface SeverityBreakdown {
  low: number
  medium: number
  high: number
  critical: number
}

export interface Analytics {
  total_prs_reviewed: number
  avg_risk_score: number | null
  avg_latency_ms: number | null
  total_cost_usd: number
  severity_breakdown: SeverityBreakdown
  weekly_bug_trend: WeeklyBugTrend[]
  weekly_cost: WeeklyCost[]
  latency_buckets: LatencyBucket[]
}
