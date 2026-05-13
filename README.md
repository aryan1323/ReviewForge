<div align="center">

# ReviewForge

**AI-powered Pull Request reviews — instant, inline, and on your dashboard.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-review--forge--gamma.vercel.app-6366f1?style=for-the-badge&logo=vercel)](https://review-forge-gamma.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react)](https://react.dev)
[![pgvector](https://img.shields.io/badge/pgvector-RAG-336791?style=flat-square&logo=postgresql)](https://github.com/pgvector/pgvector)

</div>

---

## What it does

Every time a developer opens or updates a Pull Request, ReviewForge automatically:

1. **Receives** the GitHub webhook and queues a background review job
2. **Understands your codebase** — clones and indexes the repo into a vector store (pgvector) so the AI has full context, not just the diff
3. **Reviews with AI** — sends the diff + semantically relevant code chunks to Azure OpenAI for a structured, JSON-schema review
4. **Scores risk** — computes a 0–10 risk score weighted by issue severity (critical × 4, high × 2, medium × 1, low × 0.25)
5. **Surfaces results** on a live React dashboard — no GitHub comment spam, just clean insights

---

## Live Demo

**Frontend:** [https://review-forge-gamma.vercel.app](https://review-forge-gamma.vercel.app)

Register an account, add your API keys in Settings, configure the webhook on any GitHub repo, and raise a PR — the review appears on the dashboard within seconds.

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Repository                      │
│   Developer opens PR  →  Webhook fires                  │
└───────────────────────────┬─────────────────────────────┘
                            │  POST /webhook/github/{user_id}
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│   ① Verify HMAC signature (per-user secret)              │
│   ② Upsert PR record in PostgreSQL                       │
│   ③ Enqueue job → Redis (rq)                             │
│   ④ Return 202 immediately                               │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     rq Worker                            │
│                                                          │
│  ┌──────────┐   ┌───────────┐   ┌─────────────────┐    │
│  │ RAG Index │ → │  Retrieve │ → │  Azure OpenAI   │    │
│  │ (pgvector)│   │ top-10    │   │  (o4-mini)      │    │
│  │ on 1st PR │   │ chunks by │   │  structured JSON│    │
│  └──────────┘   │ cosine sim│   │  review output  │    │
│                  └───────────┘   └────────┬────────┘    │
│                                           │              │
│  ┌────────────────────────────────────────▼──────────┐  │
│  │  Persist: Review + Comments + Metrics in Postgres  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│               React Dashboard (Vercel)                   │
│   PR list · Risk scores · Inline comments · Analytics   │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI + uvicorn | Async, fast, auto-docs |
| Task queue | rq (Redis Queue) | Lightweight, Redis-native |
| Vector store | PostgreSQL + pgvector | No extra service — reuses existing DB |
| LLM | Azure OpenAI (o4-mini) | Structured JSON output, low temp |
| Embeddings | text-embedding-3-small | Fast + cheap, 1536-dim vectors |
| Auth | JWT (python-jose) + bcrypt | Stateless, per-user API keys |
| Frontend | React 18 + Vite + Tailwind | Fast builds, clean UI |
| Hosting | Vercel + Render + Supabase + Upstash | 100% free tier |

---

## Key Features

- **Per-user accounts** — register, log in, manage your own API keys and webhook secret
- **RAG-powered context** — the AI sees relevant source files, not just the changed lines
- **Risk scoring** — every PR gets a 0–10 score so you can prioritize reviews
- **Analytics dashboard** — bug trends, token costs, latency distribution, severity breakdown
- **Public repo support** — GitHub token is optional; only needed for private repos
- **Single-service deploy** — rq worker runs as a daemon thread inside the API process (no separate worker dyno needed)

---

## Self-hosting (Docker)

```bash
# 1. Clone and configure
git clone https://github.com/aryan1323/ReviewForge.git
cd ReviewForge
cp .env.example .env
# Fill in DATABASE_URL, REDIS_URL, SECRET_KEY, and Azure OpenAI vars

# 2. Start everything
docker compose up --build

# 3. Run migrations
docker compose exec api alembic upgrade head

# Services:
#   API        →  http://localhost:8000
#   Frontend   →  http://localhost:3000
#   Prometheus →  http://localhost:9090
#   Grafana    →  http://localhost:3001  (admin / admin)
```

---

## Connecting a GitHub Repo

1. Register at the frontend and go to **Settings**
2. Add your API keys (Azure OpenAI required; GitHub token only for private repos)
3. Copy your unique **Webhook URL** from the Settings page
4. In your GitHub repo → **Settings → Webhooks → Add webhook**
   - Payload URL: *(paste the URL from Settings)*
   - Content type: `application/json`
   - Secret: *(paste the GitHub Webhook Secret you set in Settings)*
   - Events: **Pull requests** only
5. Open or reopen a PR — the review appears on your dashboard within ~30 seconds

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/webhook/github/{user_id}` | GitHub webhook receiver (HMAC verified) |
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Get JWT token |
| `GET` | `/api/prs` | List reviewed PRs (paginated, filterable) |
| `GET` | `/api/prs/{id}` | PR detail with all inline comments |
| `GET` | `/api/analytics` | Aggregated metrics (last N weeks) |
| `GET/PUT` | `/api/config` | Read / save user API keys |
| `GET` | `/health` | DB + Redis liveness check |
| `GET` | `/metrics` | Prometheus scrape endpoint |

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests use `unittest.mock` — no live DB or API calls required.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `SYNC_DATABASE_URL` | Yes | Sync URL for Alembic migrations |
| `REDIS_URL` | Yes | Redis URL (`redis://` or `rediss://` for TLS) |
| `SECRET_KEY` | Yes | JWT signing secret — use a long random string |
| `AZURE_OPENAI_API_KEY` | No* | Set globally or per-user in Settings |
| `AZURE_OPENAI_ENDPOINT` | No* | Azure OpenAI endpoint URL |
| `AZURE_DEPLOYMENT` | No* | Chat model deployment name |
| `AZURE_API_VERSION` | No* | Azure OpenAI API version |
| `AZURE_EMBEDDING_DEPLOYMENT` | No* | Embedding model deployment name |
| `GITHUB_TOKEN` | No | Global fallback token (users set their own) |
| `CORS_ORIGINS` | No | JSON list of allowed origins |

*Can be set per-user in the Settings page instead of as env vars.
