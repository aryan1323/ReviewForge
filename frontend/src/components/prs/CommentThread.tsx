import { ChevronDown, ChevronRight, FileCode } from 'lucide-react'
import { useState } from 'react'
import { SeverityBadge, CategoryBadge } from '../shared/Badge'
import type { Comment } from '../../types/pr'
import type { Severity } from '../../utils/severity'

interface Props {
  comments: Comment[]
}

export function CommentThread({ comments }: Props) {
  // Group by file
  const byFile = comments.reduce<Record<string, Comment[]>>((acc, c) => {
    ;(acc[c.file_path] ??= []).push(c)
    return acc
  }, {})

  if (comments.length === 0) {
    return <p className="text-slate-500 text-sm">No issues found.</p>
  }

  return (
    <div className="space-y-3">
      {Object.entries(byFile).map(([file, fileComments]) => (
        <FileGroup key={file} file={file} comments={fileComments} />
      ))}
    </div>
  )
}

function FileGroup({ file, comments }: { file: string; comments: Comment[] }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="border border-border rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2.5 px-4 py-3 bg-card hover:bg-white/5 transition-colors text-left"
      >
        {open ? <ChevronDown className="w-4 h-4 text-slate-500 shrink-0" /> : <ChevronRight className="w-4 h-4 text-slate-500 shrink-0" />}
        <FileCode className="w-4 h-4 text-accent shrink-0" />
        <span className="font-mono text-xs text-slate-300 flex-1 truncate">{file}</span>
        <span className="text-xs text-slate-600 shrink-0">{comments.length} issue{comments.length !== 1 ? 's' : ''}</span>
      </button>

      {open && (
        <div className="divide-y divide-border">
          {comments.map(c => (
            <CommentCard key={c.id} comment={c} />
          ))}
        </div>
      )}
    </div>
  )
}

function CommentCard({ comment: c }: { comment: Comment }) {
  return (
    <div className="px-4 py-3.5 bg-surface">
      <div className="flex items-center gap-2 mb-2">
        <CategoryBadge category={c.category} />
        <SeverityBadge severity={c.severity as Severity} />
        {c.line_number && (
          <span className="text-slate-600 text-xs font-mono">line {c.line_number}</span>
        )}
      </div>
      <p className="text-slate-300 text-sm leading-relaxed">{c.message}</p>
      {c.suggestion && (
        <pre className="mt-3 bg-sidebar border border-border rounded-lg px-4 py-3 text-xs text-slate-300 font-mono overflow-x-auto leading-relaxed">
          {c.suggestion}
        </pre>
      )}
    </div>
  )
}
