import client from './client'
import type { Analytics } from '../types/analytics'

export async function fetchAnalytics(weeks = 12): Promise<Analytics> {
  const { data } = await client.get('/api/analytics', { params: { weeks } })
  return data
}
