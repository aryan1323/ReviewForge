import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { shortWeek } from '../../utils/formatters'
import type { WeeklyBugTrend } from '../../types/analytics'

const LINES = [
  { key: 'bug_count',         label: 'Bugs',        color: '#f87171' },
  { key: 'security_count',    label: 'Security',    color: '#c084fc' },
  { key: 'performance_count', label: 'Performance', color: '#60a5fa' },
  { key: 'style_count',       label: 'Style',       color: '#94a3b8' },
]

export function BugTrendChart({ data }: { data: WeeklyBugTrend[] }) {
  const formatted = data.map(d => ({ ...d, week: shortWeek(d.week_start) }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={formatted} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
        <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
        <Tooltip
          contentStyle={{ background: '#1e2130', border: '1px solid #2a2d3e', borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: '#94a3b8' }}
        />
        <Legend wrapperStyle={{ fontSize: 11, paddingTop: 12 }} />
        {LINES.map(l => (
          <Line key={l.key} type="monotone" dataKey={l.key} name={l.label} stroke={l.color}
            strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
