import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, GitBranch, User, Clock, DollarSign } from 'lucide-react'
import { usePRDetail } from '../hooks/usePRDetail'
import { PageLoader } from '../components/shared/Spinner'
import { CommentThread } from '../components/prs/CommentThread'
import { StatusBadge, SeverityBadge } from '../components/shared/Badge'
import { RiskScore } from '../components/prs/RiskScore'
import { timeAgo, formatCost, formatMs } from '../utils/formatters'
import type { Severity } from '../utils/severity'

export function PRDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: pr, isLoading } = usePRDetail(id!)

  if (isLoading) return <PageLoader />
  if (!pr) return (
    <div className="p-6">
      <p className="text-slate-500">Pull request not found.</p>
    </div>
  )

  const latestReview = pr.reviews[0]
  const allComments = pr.reviews.flatMap(r => r.comments)

  return (
    <div className="p-6 space-y-5">
      {/* Back */}
      <Link to="/prs" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-300 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to PRs
      </Link>

      {/* Header card */}
      <div className="card space-y-4">
        <div className="flex items-start gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-slate-500 font-mono text-sm">#{pr.number}</span>
              <StatusBadge status={pr.review_status} />
              {latestReview?.overall_severity && (
                <SeverityBadge severity={latestReview.overall_severity as Severity} />
              )}
            </div>
            <h2 className="text-lg font-semibold text-slate-100 leading-snug">{pr.title}</h2>
            <p className="text-slate-500 text-sm mt-0.5 font-mono">{pr.repo_full_name}</p>
          </div>
          <a
            href={pr.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 p-2 text-slate-500 hover:text-slate-300 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>

        {/* Meta row */}
        <div className="flex items-center gap-5 text-xs text-slate-500 flex-wrap border-t border-border pt-4">
          <span className="flex items-center gap-1.5"><User className="w-3.5 h-3.5" />{pr.author}</span>
          <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />{timeAgo(pr.opened_at)}</span>
          <span className="flex items-center gap-1.5">Risk: <RiskScore score={pr.risk_score} /></span>
          {latestReview?.latency_ms && (
            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />{formatMs(latestReview.latency_ms)}</span>
          )}
          {latestReview?.total_cost_usd && (
            <span className="flex items-center gap-1.5"><DollarSign className="w-3.5 h-3.5" />{formatCost(latestReview.total_cost_usd)}</span>
          )}
        </div>

        {/* Summary */}
        {latestReview?.summary && (
          <div className="bg-sidebar border border-border rounded-lg px-4 py-3">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1.5">AI Summary</p>
            <p className="text-slate-300 text-sm leading-relaxed">{latestReview.summary}</p>
          </div>
        )}
      </div>

      {/* Token usage */}
      {latestReview && (
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Prompt tokens',     value: latestReview.prompt_tokens?.toLocaleString() ?? '—' },
            { label: 'Completion tokens', value: latestReview.completion_tokens?.toLocaleString() ?? '—' },
            { label: 'Model',             value: latestReview.model },
          ].map(item => (
            <div key={item.label} className="card py-3">
              <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1">{item.label}</p>
              <p className="text-sm font-mono text-slate-300">{item.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Comments */}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Review Comments
          <span className="ml-2 text-slate-600 font-normal">({allComments.length})</span>
        </h3>
        <CommentThread comments={allComments} />
      </div>
    </div>
  )
}
