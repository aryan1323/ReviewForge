# GitHub PR Review Bot

Automated code review bot powered by **GPT-4o** + **RAG (pgvector)**. When a developer opens a PR, the bot fetches the diff, retrieves relevant codebase context from a vector store, and posts inline review comments directly on the PR.

## Architecture

```
GitHub Webhook
      ↓
  FastAPI API  →  Redis (rq queue)
      ↓                  ↓
  PostgreSQL       rq Worker
  (pgvector)            ↓
                   1. Fetch diff (GitHub API)
                   2. RAG retrieve (pgvector cosine search)
                   3. GPT-4o review (structured JSON)
                   4. Post inline comments (GitHub API)
                   5. Store metrics → Prometheus → Grafana
```

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + uvicorn |
| Task queue | rq (Redis Queue) |
| Message broker | Redis 7 |
| Database | PostgreSQL 16 + pgvector |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions + GHCR |

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Fill in GITHUB_TOKEN, GITHUB_WEBHOOK_SECRET, OPENAI_API_KEY
```

### 2. Start all services

```bash
docker compose up --build
```

This starts: PostgreSQL (with pgvector), Redis, API, rq worker, Prometheus, Grafana.

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Register the webhook on your GitHub repo

1. Expose the API publicly (e.g. with ngrok): `ngrok http 8000`
2. GitHub repo → Settings → Webhooks → Add webhook
   - Payload URL: `https://<your-ngrok>.ngrok.io/webhook/github`
   - Content type: `application/json`
   - Secret: matches `GITHUB_WEBHOOK_SECRET` in `.env`
   - Events: **Pull requests**

### 5. Open a PR on your repo

The bot will:
- Receive the webhook → queue a review job
- Clone & index the repo into pgvector (first time only)
- Retrieve relevant code context
- Call GPT-4o for a structured review
- Post inline comments on the PR

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/webhook/github` | GitHub webhook receiver |
| `GET` | `/api/prs` | List reviewed PRs (paginated) |
| `GET` | `/api/prs/{id}` | PR detail with comments |
| `GET` | `/api/analytics` | Aggregated metrics |
| `GET` | `/health` | DB + Redis liveness check |
| `GET` | `/metrics` | Prometheus metrics |

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin / admin)

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --cov=app
```

## Environment Variables

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | Personal access token with `repo` scope |
| `GITHUB_WEBHOOK_SECRET` | HMAC secret set in GitHub webhook settings |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o + embeddings |
| `DATABASE_URL` | PostgreSQL asyncpg connection string |
| `SYNC_DATABASE_URL` | PostgreSQL sync connection string (Alembic) |
| `REDIS_URL` | Redis connection URL |
