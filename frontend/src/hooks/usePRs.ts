import { useQuery } from '@tanstack/react-query'
import { fetchPRs } from '../api/prs'

export function usePRs(params?: { repo?: string; status?: string; page?: number }) {
  return useQuery({
    queryKey: ['prs', params],
    queryFn: () => fetchPRs(params),
    refetchInterval: 30_000,
  })
}
