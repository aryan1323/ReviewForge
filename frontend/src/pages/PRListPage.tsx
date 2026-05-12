import { useState } from 'react'
import { Search } from 'lucide-react'
import { PRTable } from '../components/prs/PRTable'
import { PageLoader } from '../components/shared/Spinner'
import { usePRs } from '../hooks/usePRs'

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'pending',   label: 'Pending' },
  { value: 'reviewing', label: 'Reviewing' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed',    label: 'Failed' },
]

export function PRListPage() {
  const [status, setStatus] = useState('')
  const [repo, setRepo]     = useState('')
  const [page, setPage]     = useState(1)
  const PAGE_SIZE = 20

  const { data, isLoading } = usePRs({
    status: status || undefined,
    repo: repo || undefined,
    page,
    page_size: PAGE_SIZE,
  })

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1

  return (
    <div className="p-6 space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            value={repo}
            onChange={e => { setRepo(e.target.value); setPage(1) }}
            placeholder="Filter by repo (owner/repo)"
            className="w-full bg-card border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-accent transition-colors"
          />
        </div>

        <select
          value={status}
          onChange={e => { setStatus(e.target.value); setPage(1) }}
          className="bg-card border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-accent transition-colors cursor-pointer"
        >
          {STATUS_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>

        {data && (
          <span className="text-xs text-slate-600 ml-auto">
            {data.total} pull request{data.total !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Table */}
      <div className="card">
        {isLoading ? <PageLoader /> : <PRTable prs={data?.items ?? []} />}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-xs rounded-lg border border-border text-slate-400 hover:text-slate-200 hover:border-slate-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <span className="text-xs text-slate-500">{page} / {totalPages}</span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 text-xs rounded-lg border border-border text-slate-400 hover:text-slate-200 hover:border-slate-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
