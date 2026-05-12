import { Link } from 'react-router-dom'
import { ExternalLink, MessageSquare } from 'lucide-react'
import { SeverityBadge, StatusBadge } from '../shared/Badge'
import { RiskScore } from './RiskScore'
import { timeAgo } from '../../utils/formatters'
import { EmptyState } from '../shared/EmptyState'
import type { PRSummary } from '../../types/pr'
import type { Severity } from '../../utils/severity'

interface Props {
  prs: PRSummary[]
}

export function PRTable({ prs }: Props) {
  if (prs.length === 0) {
    return <EmptyState title="No pull requests yet" description="Open a PR on a connected repo to trigger a review." />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {['Pull Request', 'Repo', 'Risk', 'Severity', 'Status', 'Comments', 'Opened'].map(h => (
              <th key={h} className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider pb-3 pr-4">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {prs.map(pr => (
            <tr key={pr.id} className="hover:bg-white/2 transition-colors group">
              {/* Title */}
              <td className="py-3.5 pr-4 max-w-xs">
                <Link
                  to={`/prs/${pr.id}`}
                  className="text-slate-200 hover:text-accent font-medium truncate block transition-colors"
                >
                  #{pr.number} {pr.title}
                </Link>
                <span className="text-slate-600 text-xs">{pr.author}</span>
              </td>

              {/* Repo */}
              <td className="py-3.5 pr-4">
                <span className="text-slate-400 font-mono text-xs">{pr.repo_full_name}</span>
              </td>

              {/* Risk */}
              <td className="py-3.5 pr-4">
                <RiskScore score={pr.risk_score} />
              </td>

              {/* Severity */}
              <td className="py-3.5 pr-4">
                {pr.overall_severity
                  ? <SeverityBadge severity={pr.overall_severity as Severity} />
                  : <span className="text-slate-600 text-xs">—</span>
                }
              </td>

              {/* Status */}
              <td className="py-3.5 pr-4">
                <StatusBadge status={pr.review_status} />
              </td>

              {/* Comments */}
              <td className="py-3.5 pr-4">
                <span className="flex items-center gap-1 text-slate-400">
                  <MessageSquare className="w-3.5 h-3.5" />
                  {pr.comment_count}
                </span>
              </td>

              {/* Opened */}
              <td className="py-3.5">
                <span className="text-slate-500 text-xs whitespace-nowrap">{timeAgo(pr.opened_at)}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
