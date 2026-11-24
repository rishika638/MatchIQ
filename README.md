# MatchIQ — Opportunity Intelligence Engine

MatchIQ is an AI-powered SaaS platform engineered to help professionals discover engineering opportunities, evaluate compatibility transparently, understand skill gaps, and make informed career moves.

---

## 🌟 Key Differentiators & Engineering Highlights

- **8-Stage Hybrid Search**: Combines pgvector dense semantic embeddings (384-d `all-MiniLM-L6-v2`) with PostgreSQL full-text keyword retrieval via **Reciprocal Rank Fusion (RRF, k=60)**.
- **Cross-Encoder Reranking**: Configurable attention scoring using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Explainable Matching Engine**: Itemizes compatibility across Semantic Similarity, Skills Overlap, Experience Tenure, Role Relevance, and Career Preferences while keeping hard eligibility constraints separate.
- **Autonomous AI Career Copilot**: Real backend tool calling (`search_opportunities`, `get_opportunity_details`, `save_opportunity`, `compare_opportunities`, `get_candidate_profile`, `update_candidate_preferences`, `analyze_skill_gaps`) with configurable Google Gemini and deterministic offline fallback.
- **Resume Extraction**: Automated PDF and TXT text extraction, parsing technical competencies, experience tenure, and education.
- **Recommendation Feedback Loop**: Records user feedback (`relevant`, `not_relevant`, `applied`, `not_interested`) to calibrate match relevance.
- **Reproducible Evaluation Suite**: Empirical benchmarking of MRR, NDCG@K, Precision@K, Recall@K, and latencies across 4 retrieval paradigms using ground-truth relevance judgements.
- **Strict Multi-Tenant Architecture**: User and organization data isolation enforced across all database queries.

---

## 🏗️ Tech Stack

- **Frontend**: Next.js 14 App Router, React 18, TypeScript, Tailwind CSS, Lucide Icons, Recharts
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- **Database**: PostgreSQL 16, pgvector, PostgreSQL Full-Text Search
- **AI & NLP**: Sentence Transformers (384-d MiniLM), Cross-Encoder Reranker, Google GenAI SDK
- **Infrastructure**: Docker, Docker Compose, Production Dockerfiles

---

## 🚀 Quick Start with Docker Compose

To launch the complete platform (PostgreSQL with pgvector, FastAPI backend, and Next.js frontend):

```bash
# 1. Clone repository and navigate to workspace
git clone <repo_url>
cd JobMatchIQ

# 2. Configure environment (optional Gemini key for LLM mode)
cp .env.example .env

# 3. Launch Docker containers
docker-compose up --build
```

- **Frontend**: `http://localhost:3000`
- **FastAPI REST API**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/api/v1/docs`

---

## 💻 Local Development Setup (Without Docker)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database, load 100 opportunities, and run benchmarks
python scripts/init_and_seed.py

# Run FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Run Next.js App Router development server
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 👤 Pre-Seeded Demo Credentials

The database comes pre-seeded with 100 realistic technical roles across engineering domains and a pre-configured demo candidate:

- **Email**: `candidate@matchiq.ai`
- **Password**: `DemoCandidate123!`
- **Role**: Senior Full Stack & Distributed Systems Engineer

*(A quick "One-Click Fill" button is also provided on the `/auth` page for instant login).*

---

## 📊 Application Pages Overview

1. **Landing Page (`/`)**: Natural language search query box, system architecture highlights, and navigation.
2. **Authentication (`/auth`)**: JWT-based Sign In & Registration with demo candidate prefill.
3. **Intelligence Dashboard (`/dashboard`)**: Active opportunity count, saved/applied metrics, average compatibility, and target role skill gap insights.
4. **Opportunity Discovery (`/discover`)**: 8-stage hybrid retrieval, RRF scores, keyword ranks, and Cross-Encoder toggle.
5. **Opportunity Details (`/opportunities/[id]`)**: Full description, responsibilities, benefits, explainable compatibility breakdown, and recommendation feedback loop.
6. **Candidate Profile (`/profile`)**: Skills manager, resume PDF uploader with live extraction preview, and work mode preferences.
7. **AI Career Copilot (`/agent`)**: Autonomous career copilot executing real backend tools with persistent conversational memory.
8. **Application Tracker (`/saved`)**: Lifecycle stage manager (`saved`, `applied`, `interviewing`, `offered`, `archived`) with private notes.
9. **Opportunity Comparison (`/compare`)**: Side-by-side comparative matrix of 2 to 4 technical roles.
10. **Evaluation & Benchmarks (`/evaluation`)**: Interactive quantitative evaluation dashboard comparing MRR, NDCG@5, Precision@3, and Latency.
11. **Settings & Ingestion (`/settings`)**: Multi-tenant workspace overview, CSV/JSON dataset ingestion, and embedding re-indexing.

---

## 🧪 Quantitative Evaluation & Benchmarking

MatchIQ includes a real, reproducible offline evaluation pipeline with ground-truth relevance judgements (`data/evaluation/evaluation_benchmark.json`).

To trigger the benchmark run:
- **Via UI**: Navigate to `/evaluation` and click **"Run Benchmark Suite"**.
- **Via API**: `POST /api/v1/evaluation/run-suite`
- **Via CLI**: `python backend/scripts/init_and_seed.py`

Results are persisted in PostgreSQL `evaluation_runs`.

---

## 🔒 Security & Data Isolation

- PBKDF2-HMAC-SHA256 salted password hashing
- Stateless JWT bearer authentication
- Multi-tenant tenant access enforcement (`enforce_tenant_access`)
- Pydantic v2 strict input validation
- Multipart file size and MIME-type verification

---

## 📚 Technical Documentation

- [System Architecture & Multi-Stage Retrieval](docs/architecture.md)
- [REST API Reference & OpenAPI Endpoints](docs/api.md)
- [Quantitative Evaluation & Metric Formulations](docs/evaluation.md)

---

## 📄 License & Attribution

MatchIQ Opportunity Intelligence Engine is licensed under the Apache 2.0 License. All demo opportunities in `data/seed/` are synthetic records created for benchmarking and demonstration purposes.
