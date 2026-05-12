import type { ReactNode } from 'react'
import { GitPullRequest } from 'lucide-react'

interface Props {
  title: string
  description?: string
  icon?: ReactNode
}

export function EmptyState({ title, description, icon }: Props) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3 text-center">
      <div className="text-slate-600">
        {icon ?? <GitPullRequest className="w-10 h-10" />}
      </div>
      <p className="text-slate-400 font-medium">{title}</p>
      {description && <p className="text-slate-600 text-sm max-w-xs">{description}</p>}
    </div>
  )
}
