import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { shortWeek, formatCost } from '../../utils/formatters'
import type { WeeklyCost } from '../../types/analytics'

export function TokenCostChart({ data }: { data: WeeklyCost[] }) {
  const formatted = data.map(d => ({ ...d, week: shortWeek(d.week_start) }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={formatted} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" vertical={false} />
        <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false}
          tickFormatter={v => `$${v.toFixed(3)}`} />
        <Tooltip
          contentStyle={{ background: '#1e2130', border: '1px solid #2a2d3e', borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: '#94a3b8' }}
          formatter={(v: number) => [formatCost(v), 'Cost']}
        />
        <Bar dataKey="cost_usd" name="Cost" fill="#6366f1" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
