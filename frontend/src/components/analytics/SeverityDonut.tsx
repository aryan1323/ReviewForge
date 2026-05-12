import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import type { SeverityBreakdown } from '../../types/analytics'

const ENTRIES = [
  { key: 'critical', label: 'Critical', color: '#f87171' },
  { key: 'high',     label: 'High',     color: '#fb923c' },
  { key: 'medium',   label: 'Medium',   color: '#fbbf24' },
  { key: 'low',      label: 'Low',      color: '#94a3b8' },
]

export function SeverityDonut({ data }: { data: SeverityBreakdown }) {
  const chartData = ENTRIES
    .map(e => ({ name: e.label, value: data[e.key as keyof SeverityBreakdown], color: e.color }))
    .filter(e => e.value > 0)

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-[220px] text-slate-600 text-sm">No data yet</div>
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={chartData} cx="50%" cy="45%" innerRadius={55} outerRadius={85}
          paddingAngle={3} dataKey="value">
          {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#1e2130', border: '1px solid #2a2d3e', borderRadius: 8, fontSize: 12 }}
        />
        <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
