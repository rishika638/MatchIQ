# MatchIQ Final QA Report

## Summary

- **PASS:** ingestion, retrieval API, matching explainability, agent tool execution/fallback, tracker/feedback, benchmark persistence, dashboard database reconciliation, JWT/malformed input/SQL-injection checks, upload limits, CORS, reranker fallback, concurrent saves, smoke test, TypeScript, production build.
- **FAIL:** authentication-rate limiting is absent; CORS wildcard was fixed.
- **BLOCKED:** database-outage test, clean backend Docker build/reproducibility, browser UI execution, and Git status because the project root is not a Git repository.

## Evidence and Results

### 1. Ingestion

- PASS: 1 JSON, 10 CSV, 100 JSON, mixed JSON, duplicate stable IDs, and partial-invalid batch.
- PASS: mixed batch result was 2 success / 1 failure with persisted job errors.
- PASS: 100-record batch returned 100 success / 0 failed.
- PASS: BOM-prefixed JSON fixed and verified.
- PASS: unsupported `.txt` upload rejected.
- PASS: 11 MB upload rejected at 10 MB limit.
- PASS: active opportunity count reached 213 because 113 synthetic records were added to the preserved 100 seed records.
- PASS: 213 opportunity embeddings and 213 384-dimension embeddings.
- PASS: reindex processed 113 opportunities; smoke reruns passed.

### 2. Retrieval

Five live queries were executed through the live API and direct keyword, semantic, hybrid RRF (`k=60`), and reranked implementations.

| Query | Observed differences |
| --- | --- |
| Python backend engineer | Reranked promoted `qa-synthetic-001` above seed role 023. |
| distributed systems | Hybrid and reranked converged on seed IDs 012/047/032. |
| frontend react developer | All methods placed seed 009 first; reranking changed lower ranks. |
| data analyst SQL | Semantic uniquely promoted `qa-csv-007`; reranking promoted seed 007. |
| remote devops Kubernetes | Semantic and reranked rankings differed substantially from keyword and RRF. |

Hybrid API latency ranged from 32.45 ms to 56.13 ms in the five live calls. Direct reranking and benchmark reranking were materially slower on CPU.

### 3. Matching

The formula is 30% semantic, 30% skills, 15% experience, 15% role relevance, and 10% preference compatibility. Eligibility is separate.

For synthetic opportunity `qa-synthetic-001`:

- Before: overall 89.4; skills 100.0; semantic 72.2; missing skills none.
- After removing `Python` and adding `Kubernetes`: overall 76.0; skills 75.0; semantic 52.5; missing skill `Python`.

PASS: one profile skill change produced the correct explainable component and missing-skill updates.

### 4. Copilot

- PASS: search, details, save, profile lookup, preference updates, skill-gap analysis, and persisted conversation/tool-action records.
- PASS: fixed compare intent and “search then save top result” multi-step fallback.
- PASS: conversation persistence verified with 2 conversations, 22 messages, and 12 agent actions.
- PASS: rerun agent fallback used deterministic execution after Gemini 404/503 failures.
- PASS: reranker fallback independently returned 2 deterministic scores.
- BLOCKED: live Gemini success could not be confirmed because the tested account received 404/503 from available configured models.

### 5. Feedback and Tracker

- PASS: saved, status update, notes update, remove, and 2–3 opportunity comparison.
- PASS: relevant, not_relevant, applied, and not_interested feedback states persisted.
- PASS: isolated tracker count and feedback analytics reconciled.

### 6. Benchmarks

Measured persisted suite values from 10 queries and 542 relevance judgments:

| Method | MRR | NDCG@5 | Precision@3 | Precision@5 | Recall@5 | Latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Keyword | 0.1167 | 0.1763 | 0.6667 | 0.5400 | 0.0494 | 8.85 |
| Semantic | 0.9500 | 0.8022 | 1.0000 | 0.9600 | 0.1009 | 66.54 |
| Hybrid | 0.2600 | 0.1782 | 0.7000 | 0.5200 | 0.0464 | 44.03 |
| Hybrid reranked | 0.5667 | 0.6321 | 0.8333 | 0.7800 | 0.0745 | 1993.74 |

PASS: ground-truth references and evaluation runs persisted. No improvement was fabricated.

### 7. Analytics

- PASS: demo dashboard active opportunities 213 matched PostgreSQL 213.
- PASS: demo saved 1 and applied 0 matched PostgreSQL.
- PASS: dashboard feedback and work-mode values matched live database aggregates.
- PASS: no hardcoded active-opportunity or saved/applied metric found.

### 8. Security and Reliability

- PASS: invalid JWT rejected.
- PASS: malformed JSON rejected.
- PASS: SQL-injection text returned opportunity-not-found.
- PASS: isolated QA and demo saved lists remained separate.
- PASS: upload size and unsupported extension enforced.
- PASS: CORS evil origin rejected; configured localhost origin allowed.
- PASS: 10 concurrent saves returned successfully and respected uniqueness.
- PASS: reranker fallback verified.
- FAIL: 50 consecutive login requests produced 0 429 responses; no rate limiter is implemented.
- BLOCKED: database outage was not induced on shared services.
- BLOCKED: organization-isolation UI/workspaces could not be fully exercised without a second organization fixture.

### 9. Automated Quality

- PASS: `docker compose exec backend python scripts/test_smoke.py`.
- PASS: frontend TypeScript `npx tsc --noEmit`.
- PASS: `npm run build`.
- PASS: frontend lint exited successfully after fixing unescaped JSX entities and adding ESLint configuration; 4 React hook dependency warnings remain.
- FAIL/BLOCKED: repository contains no pytest test modules; `python -m pytest -q` exited with no tests collected.
- BLOCKED: clean backend Docker build did not complete due the PyTorch/CUDA dependency graph downloading several hundred MB; backend requirements and package ranges are not fully pinned.

## Bugs Fixed

- UTF-8 BOM JSON parsing.
- Added 10 MB and 10,000-record upload limits.
- Restricted ingestion jobs and reindex scope to the current organization.
- Scoped search to the current organization.
- Updated stale Gemini defaults and `.env.example`.
- Added real fallback handling for preference updates.
- Added fallback compare and search-then-save workflows.
- Replaced CORS wildcard with explicit configured origins.
- Removed hardcoded compose secret/database password defaults where environment variables are available.
- Fixed dashboard and evaluation JSX lint errors.
- Replaced fabricated evaluation documentation with measured results.
- Removed the database dump artifact `matchiq-before-reseed.sql`.

## Remaining Release Blockers

1. Implement and test authentication/API rate limiting.
2. Induce and test PostgreSQL failure behavior without deleting or resetting data.
3. Finish a clean backend Docker build and pin backend dependencies; the current requirements allow broad, changing releases.
4. Execute browser UI checks; no browser was shared to the automation session.
5. Create Git repository metadata or provide a repository for `git status`.
6. Add real backend pytest modules; the only backend test is the smoke script.
7. Resolve React Hook `useEffect` dependency warnings.
8. Validate the live Gemini function-calling loop against a healthy, accessible model and account.

## Production Build Commands

```bash
# Repository
cd E:\JobMatchIQ

# Database and application
docker compose up --build -d

# Backend smoke
docker compose exec backend python scripts/test_smoke.py

# Backend tests
cd backend
python -m pytest -q

# Frontend
cd ..\frontend
npm ci
npx tsc --noEmit
npm run lint
npm run build
npm start

# Clean container rebuild
cd ..
docker compose build --no-cache
docker compose up -d
```
