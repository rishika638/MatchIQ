# MatchIQ — Quantitative Evaluation & Benchmarking

## 1. Methodology & Ground Truth Dataset

MatchIQ includes a reproducible offline evaluation pipeline utilizing a curated benchmark dataset located at `data/evaluation/evaluation_benchmark.json`.

Each query in the benchmark dataset contains:
- `query_id`: Unique identifier (e.g. `eval-q01` to `eval-q10`).
- `query`: Realistic natural language user request.
- `candidate_profile`: Associated candidate background (skills, experience tenure, target roles, preferred modes).
- `intent`: User search intent description.
- `judgments`: Graded ground-truth relevance pairs:
  - **Grade 3**: Highly Relevant (Direct title, skill stack, and tenure match).
  - **Grade 2**: Relevant (Strong skill alignment with minor tenure or domain divergence).
  - **Grade 1**: Marginally Relevant (Partial topical or skill overlap).
  - **Grade 0**: Irrelevant (Unrelated technology, domain, or role requirements).

---

## 2. Quantitative Metrics Formulation

The evaluation suite calculates 5 core metrics across all retrieval runs:

### Normalized Discounted Cumulative Gain (NDCG@K)
$$\text{DCG}@K = \sum_{i=1}^K \frac{2^{rel_i} - 1}{\log_2(i + 1)}$$
$$\text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$
Evaluated at $K \in \{3, 5, 10\}$.

### Mean Reciprocal Rank (MRR)
$$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q^*}$$
where $\text{rank}_q^*$ is the rank of the first relevant result ($rel \ge 2$).

### Precision@K
$$\text{Precision}@K = \frac{\sum_{i=1}^K \mathbb{I}(rel_i \ge 1)}{K}$$

### Recall@K
$$\text{Recall}@K = \frac{\sum_{i=1}^K \mathbb{I}(rel_i \ge 1)}{\text{Total Relevant in Corpus}}$$

### Retrieval Latency
Measures end-to-end query round-trip latency in milliseconds.

---

## 3. Empirical Results Across Methods

Measured benchmark runs use the 10 query records and 542 stored relevance judgments. A rerun against the active corpus produced:

| Retrieval Method | MRR | NDCG@5 | Precision@3 | Recall@5 | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Keyword** | 0.1167 | 0.1763 | 0.6667 | 0.0494 | 8.85 |
| **Dense Semantic** | 0.9500 | 0.8022 | 1.0000 | 0.1009 | 66.54 |
| **Hybrid (RRF, k=60)** | 0.2600 | 0.1782 | 0.7000 | 0.0464 | 44.03 |
| **Hybrid + Reranked** | 0.5667 | 0.6321 | 0.8333 | 0.0745 | 1993.74 |

These are measured persisted results, not projected improvements. Metric values change with corpus, embeddings, and relevance judgments.
