import clsx from 'clsx'

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={clsx('animate-spin rounded-full border-2 border-border border-t-accent', className)} />
  )
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <Spinner className="w-8 h-8" />
    </div>
  )
}
