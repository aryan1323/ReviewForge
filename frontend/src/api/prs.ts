import client from './client'
import type { PRDetail, PRListResponse } from '../types/pr'

export async function fetchPRs(params?: {
  repo?: string
  status?: string
  page?: number
  page_size?: number
}): Promise<PRListResponse> {
  const { data } = await client.get('/api/prs', { params })
  return data
}

export async function fetchPR(id: string): Promise<PRDetail> {
  const { data } = await client.get(`/api/prs/${id}`)
  return data
}
