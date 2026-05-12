import clsx from 'clsx'
import { riskBg } from '../../utils/severity'

export function RiskScore({ score }: { score: number | null }) {
  if (score === null) return <span className="text-slate-600 text-sm">—</span>
  return (
    <span className={clsx('badge font-mono font-semibold text-xs', riskBg(score))}>
      {score.toFixed(1)}
    </span>
  )
}
