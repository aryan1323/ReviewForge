export type Severity = 'low' | 'medium' | 'high' | 'critical'

export const severityConfig: Record<Severity, { label: string; color: string; bg: string; dot: string }> = {
  low:      { label: 'Low',      color: 'text-slate-400', bg: 'bg-slate-700/50',   dot: 'bg-slate-400' },
  medium:   { label: 'Medium',   color: 'text-yellow-400', bg: 'bg-yellow-400/10', dot: 'bg-yellow-400' },
  high:     { label: 'High',     color: 'text-orange-400', bg: 'bg-orange-400/10', dot: 'bg-orange-400' },
  critical: { label: 'Critical', color: 'text-red-400',    bg: 'bg-red-400/10',    dot: 'bg-red-400' },
}

export function riskColor(score: number | null): string {
  if (score === null) return 'text-slate-500'
  if (score >= 7) return 'text-red-400'
  if (score >= 4) return 'text-orange-400'
  if (score >= 2) return 'text-yellow-400'
  return 'text-emerald-400'
}

export function riskBg(score: number | null): string {
  if (score === null) return 'bg-slate-700/50 text-slate-400'
  if (score >= 7) return 'bg-red-400/10 text-red-400'
  if (score >= 4) return 'bg-orange-400/10 text-orange-400'
  if (score >= 2) return 'bg-yellow-400/10 text-yellow-400'
  return 'bg-emerald-400/10 text-emerald-400'
}
