import client from './client'

export async function register(email: string, password: string) {
  const { data } = await client.post('/auth/register', { email, password })
  return data as { access_token: string }
}

export async function login(email: string, password: string) {
  const { data } = await client.post('/auth/login', { email, password })
  return data as { access_token: string }
}

export async function fetchMe() {
  const { data } = await client.get('/auth/me')
  return data as { id: string; email: string }
}
