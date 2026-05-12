import { useQuery } from '@tanstack/react-query'
import { fetchPR } from '../api/prs'

export function usePRDetail(id: string) {
  return useQuery({
    queryKey: ['pr', id],
    queryFn: () => fetchPR(id),
    enabled: !!id,
    refetchInterval: 15_000,
  })
}
