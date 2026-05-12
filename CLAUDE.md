# CLAUDE.md — PR Review Bot

Complete reference for this codebase. Read this before making any changes.

---

## What This Project Does

An automated GitHub Pull Request review bot. When a developer opens or updates a PR:
1. GitHub sends a webhook to the FastAPI backend
2. The backend validates the HMAC signature and enqueues a job via **rq** (Redis Queue)
3. The worker clones and indexes the repository into **pgvector** (RAG) on first run
4. It retrieves the most relevant code chunks via cosine similarity search
5. Sends the diff + context to **OpenAI GPT-4o** for structured JSON review
6. Posts inline comments directly on the GitHub PR
7. Stores all data in PostgreSQL and emits Prometheus metrics
8. A React dashboard shows reviewed PRs, risk scores, trends, and cost analytics

---

## Repository Layout

```
github-pr-review-bot/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app factory + lifespan
│   │   ├── config.py             # All env vars via pydantic-settings
│   │   ├── database.py           # Async SQLAlchemy engine + session
│   │   ├── dependencies.py       # get_db DI re-export
│   │   ├── models/               # SQLAlchemy ORM (6 models)
│   │   │   ├── base.py           # Base + TimestampMixin
│   │   │   ├── repository.py     # GitHub repo registration
│   │   │   ├── pull_request.py   # PR record + risk_score
│   │   │   ├── review.py         # One review run per PR push
│   │   │   ├── review_comment.py # Individual LLM-found issue
│   │   │   ├── review_metric.py  # Weekly aggregated metrics
│   │   │   └── code_chunk.py     # pgvector RAG embeddings
│   │   ├── schemas/              # Pydantic request/response shapes
│   │   │   ├── webhook.py        # GitHub webhook payload
│   │   │   ├── pull_request.py   # PR list + detail responses
│   │   │   └── analytics.py      # Analytics response
│   │   ├── routers/
│   │   │   ├── webhook.py        # POST /webhook/github
│   │   │   ├── pull_requests.py  # GET /api/prs, GET /api/prs/{id}
│   │   │   ├── analytics.py      # GET /api/analytics
│   │   │   └── health.py         # GET /health
│   │   ├── services/
│   │   │   ├── webhook_service.py  # HMAC verify + upsert PR + enqueue
│   │   │   ├── github_service.py   # Fetch diff, post review comments
│   │   │   ├── llm_service.py      # GPT-4o call + risk score formula
│   │   │   └── review_service.py   # List/detail/analytics queries
│   │   ├── rag/
│   │   │   ├── embedder.py         # text-embedding-3-small API calls
│   │   │   ├── indexer.py          # Clone repo, chunk, upsert pgvector
│   │   │   └── retriever.py        # Cosine similarity search
│   │   ├── tasks/
│   │   │   ├── queue.py            # rq Queue on Redis
│   │   │   └── review_tasks.py     # Full review pipeline job
│   │   └── metrics/
│   │       └── prometheus.py       # Counters + histograms
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_webhook.py
│   │   ├── test_llm_service.py
│   │   └── test_github_service.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── alembic.ini
│   ├── Dockerfile                  # API image
│   ├── Dockerfile.worker           # rq worker image
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # Router + layout shell
│   │   ├── main.tsx              # React + QueryClient bootstrap
│   │   ├── api/                  # axios client + typed fetch functions
│   │   ├── components/
│   │   │   ├── layout/           # Sidebar, Header
│   │   │   ├── prs/              # PRTable, CommentThread, RiskScore
│   │   │   ├── analytics/        # BugTrendChart, TokenCostChart, LatencyChart, SeverityDonut
│   │   │   └── shared/           # StatCard, Badge, Spinner, EmptyState
│   │   ├── hooks/                # usePRs, usePRDetail, useAnalytics
│   │   ├── pages/                # DashboardPage, PRListPage, PRDetailPage, AnalyticsPage
│   │   ├── types/                # pr.ts, analytics.ts
│   │   └── utils/                # formatters.ts, severity.ts
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── infrastructure/
│   ├── prometheus/prometheus.yml
│   └── grafana/
│       ├── provisioning/         # Auto-provisioned datasource + dashboard
│       └── dashboards/           # pr-review-bot.json
├── docker-compose.yml            # All 7 services
├── docker-compose.override.yml   # Dev: hot reload + bind mounts
├── .env.example
└── CLAUDE.md                     # This file
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in all values before running.

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token with `repo` scope. Used to fetch diffs and post review comments. |
| `GITHUB_WEBHOOK_SECRET` | Yes | Secret string you set in GitHub webhook settings. Used for HMAC-SHA256 signature verification. |
| `OPENAI_API_KEY` | Yes | OpenAI API key. Used for GPT-4o reviews and text-embedding-3-small embeddings. |
| `DATABASE_URL` | Yes | Async PostgreSQL URL. Format: `postgresql+asyncpg://user:pass@host:5432/db` |
| `SYNC_DATABASE_URL` | Yes | Sync PostgreSQL URL for Alembic. Format: `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Yes | Redis URL. Default: `redis://redis:6379/0` |
| `CORS_ORIGINS` | No | JSON list of allowed origins. Default: `["http://localhost:3000"]` |
| `LOG_LEVEL` | No | `DEBUG` or `INFO`. Default: `INFO` |
| `OPENAI_INPUT_COST_PER_M` | No | GPT-4o input token cost per 1M. Default: `2.50` |
| `OPENAI_OUTPUT_COST_PER_M` | No | GPT-4o output token cost per 1M. Default: `10.00` |
| `RAG_TOP_K` | No | Number of code chunks to retrieve for context. Default: `10` |
| `RAG_CHUNK_SIZE` | No | Chunk size in tokens. Default: `400` |
| `EMBEDDING_MODEL` | No | OpenAI embedding model. Default: `text-embedding-3-small` |

---

## How to Run

### Option A — Docker Compose (recommended)

**Prerequisites:** Docker + Docker Compose v2, `ngrok` for webhook testing.

```bash
# 1. Clone and enter the project
cd github-pr-review-bot

# 2. Set up environment
cp .env.example .env
# Edit .env and fill in GITHUB_TOKEN, GITHUB_WEBHOOK_SECRET, OPENAI_API_KEY

# 3. Start all services (first run builds images)
docker compose up --build

# 4. Run database migrations (in a second terminal)
docker compose exec api alembic upgrade head

# 5. Services are now running:
#    API          http://localhost:8000
#    Frontend     http://localhost:3000
#    Prometheus   http://localhost:9090
#    Grafana      http://localhost:3001  (admin / admin)
```

**Development mode** (hot reload, bind mounts):
```bash
docker compose up  # override file is loaded automatically
```
The `docker-compose.override.yml` mounts `./backend` into the container and
runs uvicorn with `--reload`, so Python changes take effect immediately.

### Option B — Local (without Docker)

**Prerequisites:** Python 3.12, Node 20, PostgreSQL 16 with pgvector extension, Redis 7.

```bash
# --- Backend ---
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Copy and fill .env in the repo root
cp ../.env.example ../.env

# Run migrations
SYNC_DATABASE_URL=postgresql://bot:bot@localhost:5432/pr_review alembic upgrade head

# Start API
uvicorn app.main:app --reload --port 8000

# Start worker (separate terminal, same venv)
rq worker reviews --url redis://localhost:6379/0

# --- Frontend ---
cd ../frontend
npm install
npm run dev   # http://localhost:3000
```

---

## Connecting a GitHub Repo (Webhook Setup)

1. Expose your local API with ngrok:
   ```bash
   ngrok http 8000
   # Copy the https URL, e.g. https://abc123.ngrok.io
   ```

2. Go to your GitHub repo → **Settings** → **Webhooks** → **Add webhook**
   - Payload URL: `https://abc123.ngrok.io/webhook/github`
   - Content type: `application/json`
   - Secret: paste the value of `GITHUB_WEBHOOK_SECRET` from your `.env`
   - Events: select **Pull requests** only
   - Click **Add webhook**

3. Open a Pull Request on that repo. The bot will:
   - Receive the webhook → return 202 immediately
   - Enqueue a review job in Redis
   - Worker picks it up, clones + indexes the repo (first time only)
   - Retrieves relevant code chunks from pgvector
   - Calls GPT-4o with diff + context
   - Posts inline review comments on the PR
   - Updates the dashboard

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/webhook/github` | HMAC header | Receives GitHub events. Validates `X-Hub-Signature-256`, enqueues review job, returns 202. |
| `GET` | `/api/prs` | None | Paginated PR list. Query params: `repo`, `status`, `page`, `page_size`. |
| `GET` | `/api/prs/{id}` | None | Full PR detail with all reviews and inline comments. |
| `GET` | `/api/analytics` | None | Aggregated metrics. Query param: `weeks` (default 12). |
| `GET` | `/health` | None | Liveness check. Pings DB and Redis. Returns 200 if both ok. |
| `GET` | `/metrics` | None | Prometheus scrape endpoint. |

---

## Database Schema

Managed by Alembic. Migration file: `alembic/versions/0001_initial_schema.py`.

| Table | Purpose |
|---|---|
| `repositories` | One row per GitHub repo. Stores `github_id`, `full_name`, `webhook_secret`. |
| `pull_requests` | One row per PR. Stores `risk_score`, `review_status`, `head_sha`. |
| `reviews` | One row per review run (a PR can be re-reviewed on each push). Stores token counts, cost, latency. |
| `review_comments` | One row per LLM-found issue. Stores `file_path`, `line_number`, `category`, `severity`, `message`, `suggestion`. |
| `review_metrics` | Weekly aggregated counts for the analytics API. |
| `code_chunks` | pgvector table. One row per ~400-token chunk of repo source code. `embedding vector(1536)`. |

The `code_chunks` table uses an `ivfflat` index for fast cosine similarity search:
```sql
CREATE INDEX idx_code_chunks_embedding
    ON code_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## How the RAG Pipeline Works

1. **Index** (`rag/indexer.py`) — triggered automatically on first webhook for a new repo:
   - Shallow-clones the repo using GitPython
   - Walks all source files (`.py`, `.ts`, `.js`, `.go`, `.java`, `.rs`, `.yaml`, etc.)
   - Skips hidden dirs, `node_modules`, files over 100 KB
   - Splits each file into overlapping 400-token chunks using `tiktoken` (`cl100k_base`)
   - Embeds chunks in batches of 500 via `text-embedding-3-small`
   - Upserts into `code_chunks` (ON CONFLICT updates embedding + content)

2. **Retrieve** (`rag/retriever.py`) — on every review:
   - Embeds the incoming diff text
   - Runs cosine similarity search against `code_chunks` for the specific repo
   - Returns top-10 chunks with their file paths and similarity scores

3. **Augment** (`services/llm_service.py`) — prepends context to the GPT-4o prompt:
   ```
   ## Relevant Repository Context
   // src/auth.py (similarity: 0.921)
   <chunk content>
   ---
   // src/models/user.py (similarity: 0.887)
   <chunk content>

   ## Pull Request Diff
   <raw unified diff>
   ```

---

## How the LLM Review Works

- **Model:** `gpt-4o` with `response_format: {type: "json_object"}`
- **Temperature:** 0.2 (low randomness for consistent structured output)
- GPT-4o returns a JSON object with this schema:
  ```json
  {
    "summary": "2-3 sentence assessment",
    "overall_severity": "low|medium|high|critical",
    "issues": [
      {
        "file_path": "src/auth.py",
        "line_number": 42,
        "category": "security|bug|performance|style|suggestion",
        "severity": "low|medium|high|critical",
        "message": "what is wrong",
        "suggestion": "how to fix it"
      }
    ]
  }
  ```
- **Risk score formula:**
  ```
  weighted_sum = critical×4 + high×2 + medium×1 + low×0.25
  risk_score   = min((weighted_sum / issue_count) × 2.5, 10.0)
  ```
- **Cost tracking:** `prompt_tokens × $2.50/1M + completion_tokens × $10.00/1M`

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests use `unittest.mock` — no live DB or API calls required.

| Test file | What it covers |
|---|---|
| `test_webhook.py` | HMAC verification (pass + fail), ignored events/actions |
| `test_llm_service.py` | Structured JSON parsing, risk score formula, cost calculation |
| `test_github_service.py` | Diff fetching, comment body formatting with/without suggestions |

---

## Docker Services

| Service | Image | Port | Role |
|---|---|---|---|
| `postgres` | `pgvector/pgvector:pg16` | 5432 | Database + pgvector extension |
| `redis` | `redis:7-alpine` | 6379 | rq job broker |
| `api` | `./backend/Dockerfile` | 8000 | FastAPI backend |
| `worker` | `./backend/Dockerfile.worker` | — | rq worker (`reviews` queue) |
| `frontend` | `./frontend/Dockerfile` | 3000 | React dashboard (nginx) |
| `prometheus` | `prom/prometheus` | 9090 | Metrics scraping |
| `grafana` | `grafana/grafana` | 3001 | Dashboards (admin/admin) |

All services share the `bot-network` bridge network. Postgres and Redis use named volumes for persistence.

### Useful Docker commands

```bash
# View logs for a specific service
docker compose logs -f worker
docker compose logs -f api

# Restart a single service after code change
docker compose restart api

# Run a one-off migration
docker compose exec api alembic upgrade head

# Connect to the database
docker compose exec postgres psql -U bot -d pr_review

# Connect to Redis and inspect queue
docker compose exec redis redis-cli
> LLEN rq:queue:reviews     # pending jobs
> LLEN rq:finished          # completed jobs

# Rebuild images after dependency changes
docker compose build --no-cache api worker
```

---

## Prometheus Metrics

All exposed at `GET /metrics`. Scraped by Prometheus every 15s.

| Metric | Type | Labels | Description |
|---|---|---|---|
| `pr_reviews_total` | Counter | `status` | Total review runs (completed / failed) |
| `pr_review_latency_ms` | Histogram | — | End-to-end review duration in ms |
| `pr_tokens_total` | Counter | `type` (input/output) | OpenAI tokens consumed |
| `pr_cost_usd_total` | Counter | — | Total USD spent on LLM calls |
| `pr_issues_total` | Counter | `category`, `severity` | Issues found per category/severity |
| `rag_chunks_indexed_total` | Counter | — | Code chunks indexed into pgvector |

Grafana dashboard auto-provisions at startup from `infrastructure/grafana/dashboards/pr-review-bot.json`.

---

## CI/CD (GitHub Actions)

`.github/workflows/ci-cd.yml` — runs on every push and PR to `main`.

```
push → test → build (images) → deploy
         ↓
   pytest + coverage
         ↓
   docker buildx → push to GHCR
         ↓
   SSH to server → docker compose pull && up -d
```

**Required repository secrets for deployment:**

| Secret | Value |
|---|---|
| `DEPLOY_HOST` | SSH host of your server |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_SSH_KEY` | Private SSH key |

Images are pushed to `ghcr.io/{owner}/pr-review-bot-api` and `-worker`.

---

## Frontend Pages

| URL | Page | Description |
|---|---|---|
| `/` | Dashboard | Stat cards (PRs reviewed, avg risk, cost, latency) + issue trend chart + recent PRs |
| `/prs` | PR List | Filterable by repo and status, paginated, sortable table with risk scores |
| `/prs/:id` | PR Detail | Full PR info, AI summary, token stats, inline comments grouped by file |
| `/analytics` | Analytics | 4 charts: bug trend, cost/week, latency distribution, severity donut |

Auto-refreshes: PR list every 30s, PR detail every 15s, analytics every 60s.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **rq over Celery** | Lighter, Redis-native, no broker abstraction layer, ~10 lines of setup vs hundreds |
| **pgvector over Chroma/Qdrant** | Reuses existing PostgreSQL — no extra container or service |
| **GPT-4o `json_object` mode** | Guarantees valid JSON output without prompt-hacking tricks |
| **Bulk GitHub review** | All comments posted in one API call (POST `/pulls/{n}/reviews`) to avoid rate limiting |
| **Shallow clone for indexing** | `depth=1` keeps clone fast even for large repos |
| **Signature verified before DB write** | HMAC check happens before any upsert to prevent spoofed repo registration |
| **asyncio.run() in rq job** | rq workers are sync; `asyncio.run()` lets the job call async services cleanly |
