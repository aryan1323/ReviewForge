import { BarChart3, TrendingUp, DollarSign, Layers } from 'lucide-react'
import { BugTrendChart } from '../components/analytics/BugTrendChart'
import { TokenCostChart } from '../components/analytics/TokenCostChart'
import { LatencyChart } from '../components/analytics/LatencyChart'
import { SeverityDonut } from '../components/analytics/SeverityDonut'
import { PageLoader } from '../components/shared/Spinner'
import { useAnalytics } from '../hooks/useAnalytics'
import { useState } from 'react'

const WEEK_OPTIONS = [4, 8, 12, 24, 52]

export function AnalyticsPage() {
  const [weeks, setWeeks] = useState(12)
  const { data, isLoading } = useAnalytics(weeks)

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-500">Aggregated review intelligence</p>
        <select
          value={weeks}
          onChange={e => setWeeks(Number(e.target.value))}
          className="bg-card border border-border rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-accent transition-colors cursor-pointer"
        >
          {WEEK_OPTIONS.map(w => <option key={w} value={w}>Last {w} weeks</option>)}
        </select>
      </div>

      {isLoading ? <PageLoader /> : (
        <>
          {/* Summary row */}
          <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
            {[
              { label: 'PRs Reviewed',   value: data?.total_prs_reviewed ?? 0 },
              { label: 'Avg Risk Score', value: data?.avg_risk_score?.toFixed(1) ?? '—' },
              { label: 'Avg Latency',    value: data?.avg_latency_ms ? `${(data.avg_latency_ms / 1000).toFixed(1)}s` : '—' },
              { label: 'Total Cost',     value: data ? `$${data.total_cost_usd.toFixed(4)}` : '—' },
            ].map(item => (
              <div key={item.label} className="card">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">{item.label}</p>
                <p className="text-2xl font-semibold text-slate-100">{item.value}</p>
              </div>
            ))}
          </div>

          {/* Charts grid */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-4 h-4 text-accent" />
                <h2 className="text-sm font-semibold text-slate-200">Issue Trend by Category</h2>
              </div>
              <BugTrendChart data={data?.weekly_bug_trend ?? []} />
            </div>

            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm font-semibold text-slate-200">LLM Cost per Week</h2>
              </div>
              <TokenCostChart data={data?.weekly_cost ?? []} />
            </div>

            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <BarChart3 className="w-4 h-4 text-blue-400" />
                <h2 className="text-sm font-semibold text-slate-200">Review Latency Distribution</h2>
              </div>
              <LatencyChart data={data?.latency_buckets ?? []} />
            </div>

            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Layers className="w-4 h-4 text-orange-400" />
                <h2 className="text-sm font-semibold text-slate-200">Severity Breakdown</h2>
              </div>
              <SeverityDonut data={data?.severity_breakdown ?? { low: 0, medium: 0, high: 0, critical: 0 }} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
