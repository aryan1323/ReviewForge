import { useQuery } from '@tanstack/react-query'
import { fetchAnalytics } from '../api/analytics'

export function useAnalytics(weeks = 12) {
  return useQuery({
    queryKey: ['analytics', weeks],
    queryFn: () => fetchAnalytics(weeks),
    refetchInterval: 60_000,
  })
}
