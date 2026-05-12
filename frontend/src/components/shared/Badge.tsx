import clsx from 'clsx'
import { severityConfig, type Severity } from '../../utils/severity'

interface SeverityBadgeProps {
  severity: Severity
  className?: string
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const cfg = severityConfig[severity]
  return (
    <span className={clsx('badge', cfg.bg, cfg.color, className)}>
      <span className={clsx('w-1.5 h-1.5 rounded-full', cfg.dot)} />
      {cfg.label}
    </span>
  )
}

interface StatusBadgeProps {
  status: string
  className?: string
}

const statusStyles: Record<string, string> = {
  pending:   'bg-slate-700/50 text-slate-400',
  reviewing: 'bg-blue-400/10 text-blue-400',
  completed: 'bg-emerald-400/10 text-emerald-400',
  failed:    'bg-red-400/10 text-red-400',
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const style = statusStyles[status] ?? statusStyles.pending
  return (
    <span className={clsx('badge capitalize', style, className)}>
      {status}
    </span>
  )
}

export function CategoryBadge({ category }: { category: string }) {
  const styles: Record<string, string> = {
    bug:         'bg-red-400/10 text-red-400',
    security:    'bg-purple-400/10 text-purple-400',
    performance: 'bg-blue-400/10 text-blue-400',
    style:       'bg-slate-700/50 text-slate-400',
    suggestion:  'bg-teal-400/10 text-teal-400',
  }
  return (
    <span className={clsx('badge capitalize', styles[category] ?? styles.suggestion)}>
      {category}
    </span>
  )
}
