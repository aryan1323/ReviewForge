import clsx from 'clsx'
import type { LucideIcon } from 'lucide-react'

interface Props {
  label: string
  value: string | number
  sub?: string
  icon: LucideIcon
  iconColor?: string
  trend?: 'up' | 'down' | 'neutral'
}

export function StatCard({ label, value, sub, icon: Icon, iconColor = 'text-accent' }: Props) {
  return (
    <div className="card flex items-start gap-4">
      <div className={clsx('p-2.5 rounded-lg bg-white/5', iconColor)}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-1">{label}</p>
        <p className="text-2xl font-semibold text-slate-100 leading-none">{value}</p>
        {sub && <p className="text-slate-500 text-xs mt-1">{sub}</p>}
      </div>
    </div>
  )
}
