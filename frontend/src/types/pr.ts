export interface PRSummary {
  id: string
  repo_full_name: string
  number: number
  title: string
  author: string
  risk_score: number | null
  review_status: 'pending' | 'reviewing' | 'completed' | 'failed'
  overall_severity: 'low' | 'medium' | 'high' | 'critical' | null
  comment_count: number
  html_url: string
  opened_at: string
  reviewed_at: string | null
}

export interface PRListResponse {
  items: PRSummary[]
  total: number
  page: number
  page_size: number
}

export interface Comment {
  id: string
  file_path: string
  line_number: number | null
  category: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  suggestion: string | null
}

export interface ReviewDetail {
  id: string
  status: string
  model: string
  summary: string | null
  overall_severity: string | null
  prompt_tokens: number | null
  completion_tokens: number | null
  total_cost_usd: number | null
  latency_ms: number | null
  reviewed_at: string | null
  comments: Comment[]
}

export interface PRDetail {
  id: string
  repo_full_name: string
  number: number
  title: string
  author: string
  risk_score: number | null
  review_status: string
  html_url: string
  opened_at: string
  reviews: ReviewDetail[]
}
