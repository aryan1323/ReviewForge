import { Link } from 'react-router-dom'
import { GitPullRequest, AlertTriangle, DollarSign, Clock, TrendingUp } from 'lucide-react'
import { StatCard } from '../components/shared/StatCard'
import { PageLoader } from '../components/shared/Spinner'
import { PRTable } from '../components/prs/PRTable'
import { BugTrendChart } from '../components/analytics/BugTrendChart'
import { usePRs } from '../hooks/usePRs'
import { useAnalytics } from '../hooks/useAnalytics'
import { formatCost, formatMs } from '../utils/formatters'

export function DashboardPage() {
  const { data: prs, isLoading: prsLoading } = usePRs({ page: 1, page_size: 5 })
  const { data: analytics, isLoading: analyticsLoading } = useAnalytics(12)

  return (
    <div className="p-6 space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          label="PRs Reviewed"
          value={analytics?.total_prs_reviewed ?? '—'}
          icon={GitPullRequest}
          iconColor="text-accent"
        />
        <StatCard
          label="Avg Risk Score"
          value={analytics?.avg_risk_score != null ? analytics.avg_risk_score.toFixed(1) : '—'}
          sub="out of 10"
          icon={AlertTriangle}
          iconColor="text-orange-400"
        />
        <StatCard
          label="Total LLM Cost"
          value={analytics ? formatCost(analytics.total_cost_usd) : '—'}
          sub="last 12 weeks"
          icon={DollarSign}
          iconColor="text-emerald-400"
        />
        <StatCard
          label="Avg Latency"
          value={analytics?.avg_latency_ms != null ? formatMs(analytics.avg_latency_ms) : '—'}
          sub="per review"
          icon={Clock}
          iconColor="text-blue-400"
        />
      </div>

      {/* Bug trend */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-accent" />
            <h2 className="text-sm font-semibold text-slate-200">Issue Trend</h2>
          </div>
          <Link to="/analytics" className="text-xs text-slate-500 hover:text-accent transition-colors">
            View all &rarr;
          </Link>
        </div>
        {analyticsLoading
          ? <div className="h-[220px] flex items-center justify-center"><span className="text-slate-600 text-sm">Loading…</span></div>
          : <BugTrendChart data={analytics?.weekly_bug_trend ?? []} />
        }
      </div>

      {/* Recent PRs */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <GitPullRequest className="w-4 h-4 text-accent" />
            <h2 className="text-sm font-semibold text-slate-200">Recent Pull Requests</h2>
          </div>
          <Link to="/prs" className="text-xs text-slate-500 hover:text-accent transition-colors">
            View all &rarr;
          </Link>
        </div>
        {prsLoading ? <PageLoader /> : <PRTable prs={prs?.items ?? []} />}
      </div>
    </div>
  )
}
