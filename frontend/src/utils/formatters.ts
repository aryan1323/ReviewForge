import { formatDistanceToNow, format } from 'date-fns'

export function timeAgo(iso: string): string {
  return formatDistanceToNow(new Date(iso), { addSuffix: true })
}

export function shortDate(iso: string): string {
  return format(new Date(iso), 'MMM d, yyyy')
}

export function formatCost(usd: number): string {
  return `$${usd.toFixed(4)}`
}

export function formatMs(ms: number): string {
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`
}

export function shortWeek(iso: string): string {
  return format(new Date(iso), 'MMM d')
}
