import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, GitPullRequest, BarChart3, Bot, Activity, Settings, LogOut } from 'lucide-react'
import clsx from 'clsx'
import { useAuth } from '../../context/AuthContext'

const nav = [
  { to: '/',          label: 'Dashboard',    icon: LayoutDashboard },
  { to: '/prs',       label: 'Pull Requests', icon: GitPullRequest },
  { to: '/analytics', label: 'Analytics',    icon: BarChart3 },
  { to: '/settings',  label: 'Settings',     icon: Settings },
]

export function Sidebar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

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

      {/* Footer */}
      <div className="px-3 py-4 border-t border-border space-y-1">
        <div className="flex items-center gap-2 px-3 py-1">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs text-slate-500">Worker active</span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
