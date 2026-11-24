# MatchIQ Deployment Guide: Vercel + Render

## Architecture

- **Frontend:** Vercel, Next.js 14 App Router
- **Backend:** Render Web Service, Dockerized FastAPI
- **Database:** Render PostgreSQL with pgvector
- **Health check:** `GET /health`

## Render PostgreSQL

1. Create a PostgreSQL 16 database in Render.
2. Enable the pgvector extension in a database user session:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Copy the **Internal Database URL** for the backend service. Render commonly exposes it as `postgres://...`; the backend normalizes this to `postgresql+psycopg2://...`.

## Render Web Service

Use these dashboard values:

| Setting | Value |
| --- | --- |
| Repository root | repository root (leave blank) |
| Runtime | Docker |
| Dockerfile path | `backend/Dockerfile` |
| Docker build context | repository root |
| Health check path | `/health` |
| Docker port | Render assigns `$PORT` |
| Start command override | `sh -c "python scripts/migrate.py && python scripts/init_and_seed.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"` |

The Dockerfile binds to `${PORT:-10000}` and also listens on `0.0.0.0`.

Required environment variables:

| Variable | Source | Example |
| --- | --- | --- |
| `ENVIRONMENT` | Fixed production setting | `production` |
| `SECRET_KEY` | Generate outside source | `openssl rand -hex 32` |
| `DATABASE_URL` | Render PostgreSQL Internal Database URL | Render dashboard |
| `BACKEND_CORS_ORIGINS` | Exact Vercel origin(s), comma separated | `https://matchiq.vercel.app` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Deployment choice | `10080` |
| `EMBEDDING_MODEL_NAME` | Fixed model | `all-MiniLM-L6-v2` |
| `RERANKER_MODEL_NAME` | Fixed model | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| `GEMINI_API_KEY` | Gemini secret, optional | Provider secret |
| `GEMINI_MODEL` | Optional model setting | `gemini-3.8-flash` |

Never set `BACKEND_CORS_ORIGINS=*`. Never place secrets in `.env.example`, Dockerfiles, compose files, or source.

## Vercel Frontend

Use these dashboard values:

| Setting | Value |
| --- | --- |
| Framework preset | Next.js |
| Root directory | `frontend` |
| Install command | `npm ci` |
| Build command | `npm run build` |
| Output | Vercel managed Next.js output |

Set:

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | `https://<render-service-name>.onrender.com/api/v1` |

Redeploy after adding this variable. Production builds require this variable.

The final Vercel origin must be added exactly to `BACKEND_CORS_ORIGINS` on Render, including the `https://` scheme and without a trailing slash. Add preview deployment origins separately if required.

## Migration and Initialization

The backend migration command creates/updates tables, not demo users:

```bash
cd backend
alembic upgrade head
python scripts/migrate.py
python scripts/init_and_seed.py
```

Fresh PostgreSQL verification sequence:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

```bash
cd backend
export DATABASE_URL='postgresql+psycopg2://...'
alembic upgrade head
python scripts/init_and_seed.py
```

This loads the original 100 seed opportunities and 10 benchmark queries only when the opportunity table is empty. It creates no demo credentials and no QA synthetic records.

Local demonstration seeding is explicit:

```bash
cd backend
python scripts/init_and_seed.py --demo
```

Optional benchmark run generation:

```bash
python scripts/init_and_seed.py --run-benchmarks
```

Do not run `--demo` against production.

## Deployment Order

1. Create Render PostgreSQL.
2. Run `CREATE EXTENSION IF NOT EXISTS vector`.
3. Configure and deploy the Render Web Service.
4. Verify `GET /health` returns HTTP 200 and `"database":"connected"`.
5. Configure `NEXT_PUBLIC_API_URL` on Vercel.
6. Configure the exact Vercel origin on Render.
7. Redeploy the frontend.

## Post-Deploy Smoke Tests

```bash
curl https://<render-host>/health

curl -X POST https://<render-host>/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"one-time-test@example.com","password":"StrongPassword123!","full_name":"Deployment Test"}'

curl https://<render-host>/api/v1/evaluation/runs
curl https://<render-host>/api/v1/opportunities/
```

Remove the test account through the database or by future account-management tooling. Do not reset the database or preserve demo credentials in production.

Browser final verification:

1. Open the Vercel URL.
2. Register or sign in.
3. Open `/discover` and run a search.
4. Open `/profile`, `/saved`, `/agent`, `/evaluation`, and `/dashboard`.
5. Confirm requests use the Render `NEXT_PUBLIC_API_URL`.
6. Confirm no browser CORS error.

## Rollback

Backend:

```bash
git revert <commit>
git push origin main
```

Redeploy the previous Render commit. Alembic migrations are additive for the current schema; only roll back a migration after database-specific review:

```bash
cd backend
alembic downgrade -1
```

Frontend: restore the previous Vercel deployment through Vercel dashboard or redeploy the prior Git commit.

Database: restore only an independently managed Render PostgreSQL backup or snapshot. Do not delete volumes or reset local databases.

## Troubleshooting

- **Health 503:** verify `DATABASE_URL`, pgvector extension, network access, and PostgreSQL availability.
- **CORS error:** set exact Vercel origin(s), no wildcard, no trailing slash.
- **Missing migration:** run `CREATE EXTENSION IF NOT EXISTS vector` and `python scripts/migrate.py`.
- **Gemini unavailable:** deterministic fallback remains active; set a valid provider model/key.
- **Cold-start embedding latency:** the CPU model loads on first use; keep a health check and appropriate Render instance sizing.
- **Frontend API localhost:** `NEXT_PUBLIC_API_URL` was not set or Vercel needs redeployment.
- **Rate limit 429:** login is limited to 10 requests/minute/IP and registration to 5/minute/IP.
