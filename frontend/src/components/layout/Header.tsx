import { useLocation } from 'react-router-dom'
import { RefreshCw } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

const titles: Record<string, string> = {
  '/':          'Dashboard',
  '/prs':       'Pull Requests',
  '/analytics': 'Analytics',
}

export function Header() {
  const { pathname } = useLocation()
  const qc = useQueryClient()
  const [spinning, setSpinning] = useState(false)

  // match /prs/:id
  const title = pathname.startsWith('/prs/')
    ? 'PR Detail'
    : (titles[pathname] ?? 'PR Review Bot')

  function refresh() {
    setSpinning(true)
    qc.invalidateQueries().then(() => setSpinning(false))
  }

  return (
    <header className="h-14 border-b border-border flex items-center justify-between px-6 bg-surface shrink-0">
      <h1 className="text-sm font-semibold text-slate-200">{title}</h1>
      <button
        onClick={refresh}
        className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${spinning ? 'animate-spin' : ''}`} />
        Refresh
      </button>
    </header>
  )
}
