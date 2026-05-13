import client from './client'

export interface UserConfig {
  github_token: string | null
  github_webhook_secret: string | null
  azure_openai_api_key: string | null
  azure_openai_endpoint: string | null
  azure_deployment: string | null
  azure_api_version: string | null
  azure_embedding_deployment: string | null
  webhook_url: string | null
}

export async function fetchConfig(): Promise<UserConfig> {
  const { data } = await client.get('/api/config')
  return data
}

export async function saveConfig(config: Partial<Omit<UserConfig, 'webhook_url'>>): Promise<UserConfig> {
  const { data } = await client.put('/api/config', config)
  return data
}
