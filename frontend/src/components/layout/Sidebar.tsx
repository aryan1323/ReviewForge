import { NavLink } from 'react-router-dom'
import { LayoutDashboard, GitPullRequest, BarChart3, Bot, Activity } from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { to: '/',          label: 'Dashboard',   icon: LayoutDashboard },
  { to: '/prs',       label: 'Pull Requests', icon: GitPullRequest },
  { to: '/analytics', label: 'Analytics',   icon: BarChart3 },
]

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-sidebar border-r border-border flex flex-col min-h-screen">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-border">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center shrink-0">
          <Bot className="w-4.5 h-4.5 text-white" size={18} />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-100 leading-none">PR Bot</p>
          <p className="text-[10px] text-slate-500 mt-0.5">Code Review AI</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-accent/15 text-accent'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              )
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Status indicator */}
      <div className="px-5 py-4 border-t border-border">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs text-slate-500">Worker active</span>
        </div>
      </div>
    </aside>
  )
}
