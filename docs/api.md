# MatchIQ — REST API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive Swagger UI: `http://localhost:8000/api/v1/docs`

---

## 1. Authentication (`/auth`)

### `POST /auth/register`
Creates user, organization workspace, and candidate profile.
- **Body**: `{ "email": "...", "password": "...", "full_name": "..." }`
- **Response**: `{ "access_token": "...", "token_type": "bearer", "user": { ... } }`

### `POST /auth/login`
Authenticates candidate or admin credentials.
- **Body**: `{ "email": "candidate@matchiq.ai", "password": "DemoCandidate123!" }`
- **Response**: JWT access token and user metadata.

### `GET /auth/me`
Fetches active user details (Requires `Authorization: Bearer <token>`).

---

## 2. Candidate Intelligence (`/candidates`)

### `GET /candidates/profile`
Retrieves candidate profile, extracted skills, and preference constraints.

### `PUT /candidates/profile`
Updates profile headline, skills list, experience years, and career preferences.

### `POST /candidates/resume/upload`
Uploads PDF or TXT resume file (multipart/form-data), parses text, and returns extracted technical competencies and tenure.

---

## 3. Hybrid Search & Retrieval (`/search`)

### `POST /search/`
Executes 8-stage hybrid retrieval.
- **Body**:
  ```json
  {
    "query": "I want a backend engineering internship involving Python, distributed systems and AI",
    "locations": ["Seattle, WA"],
    "work_modes": ["hybrid", "remote"],
    "opportunity_types": ["internship"],
    "min_salary": 80000,
    "enable_reranking": true,
    "page": 1,
    "page_size": 15
  }
  ```
- **Response**: Total matches, latency in milliseconds, RRF scores, cosine similarities, cross-encoder scores, and itemized compatibility breakdowns.

---

## 4. Opportunity Intelligence (`/opportunities`)

### `GET /opportunities/`
Lists active opportunities with optional filtering.

### `GET /opportunities/{id}`
Returns opportunity description, requirements, benefits, and candidate explainability breakdown.

### `POST /opportunities/compare`
Compares 2 to 4 opportunities side by side across skills, compensation, and compatibility.

---

## 5. AI Career Copilot (`/agent`)

### `POST /agent/chat`
Sends user message, executes appropriate backend tools, and persists conversation turns.
- **Body**: `{ "message": "Analyze skill gaps for opp-seed-002", "conversation_id": null }`
- **Response**: Assistant response, tools executed, and engine used.

### `GET /agent/conversations`
Lists past conversations.

### `GET /agent/conversations/{id}/messages`
Retrieves chat history for a session.

---

## 6. Recommendation Feedback Loop (`/feedback`)

### `POST /feedback/`
Submits user feedback: `relevant`, `not_relevant`, `applied`, `not_interested`.

### `GET /feedback/analytics`
Returns feedback distribution and positive relevance ratio.

---

## 7. Opportunity Tracker (`/saved`)

### `GET /saved/`
Lists tracked opportunities (filters: `saved`, `applied`, `interviewing`, `offered`, `archived`).

### `POST /saved/`
Saves an opportunity with optional personal notes.

### `PATCH /saved/{id}`
Updates opportunity lifecycle stage.

### `DELETE /saved/{id}`
Removes opportunity from tracker.

---

## 8. Evaluation & Benchmarking (`/evaluation`)

### `GET /evaluation/benchmark-queries`
Returns labelled ground-truth evaluation queries.

### `POST /evaluation/run-suite`
Executes and benchmarks all 4 retrieval methods.

### `GET /evaluation/runs`
Lists historical evaluation runs with MRR, NDCG@K, Precision@K, Recall@K, and latencies.

---

## 9. Analytics & Ingestion (`/analytics`, `/ingestion`)

### `GET /analytics/dashboard`
Returns live metrics: active opportunities, average compatibility, missing skills, work mode distribution.

### `POST /ingestion/upload`
Uploads CSV or JSON opportunity dataset. Limits: 10 MB and 10,000 records.

### `POST /ingestion/reindex`
Re-indexes dense vector embeddings for all opportunities.
