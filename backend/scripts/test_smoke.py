import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def run_smoke_test():
    client = TestClient(app)
    
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] /health endpoint")

    # 2. Login as Demo Candidate
    login_res = client.post("/api/v1/auth/login", json={
        "email": "candidate@matchiq.ai",
        "password": "DemoCandidate123!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_data = login_res.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] /api/v1/auth/login")

    # 3. Get Candidate Profile
    profile_res = client.get("/api/v1/candidates/profile", headers=headers)
    assert profile_res.status_code == 200, f"Profile failed: {profile_res.text}"
    profile = profile_res.json()
    assert profile["headline"] is not None
    print(f"[PASS] /api/v1/candidates/profile (User: {profile['headline']})")

    # 4. Perform Hybrid Search
    search_res = client.post("/api/v1/search/", json={
        "query": "I want a backend engineering internship involving Python, distributed systems and AI",
        "enable_reranking": True,
        "page": 1,
        "page_size": 5
    }, headers=headers)
    assert search_res.status_code == 200, f"Search failed: {search_res.text}"
    search_data = search_res.json()
    assert search_data["total_matches"] > 0
    top_opp = search_data["results"][0]
    print(f"[PASS] /api/v1/search/ (Top match: '{top_opp['opportunity']['title']}' at {top_opp['opportunity']['company']}, RRF: {top_opp['retrieval_meta']['rrf_score']}, Compatibility: {top_opp['compatibility']['overall_compatibility']}%)")

    # 5. Opportunity Details & Explainability
    opp_id = top_opp["opportunity"]["id"]
    opp_res = client.get(f"/api/v1/opportunities/{opp_id}", headers=headers)
    assert opp_res.status_code == 200
    opp_data = opp_res.json()
    assert "compatibility" in opp_data
    print(f"[PASS] /api/v1/opportunities/{opp_id} (Explanation: {opp_data['compatibility']['explanation'][:80]}...)")

    # 6. Save Opportunity
    save_res = client.post("/api/v1/saved/", json={"opportunity_id": opp_id, "status": "saved"}, headers=headers)
    assert save_res.status_code == 200
    print(f"[PASS] /api/v1/saved/ (Saved {opp_id})")

    # 7. Agent Chat Turn (Real Tool Execution)
    agent_res = client.post("/api/v1/agent/chat", json={
        "message": f"Analyze skill gaps for {opp_id}"
    }, headers=headers)
    assert agent_res.status_code == 200, f"Agent failed: {agent_res.text}"
    agent_data = agent_res.json()
    assert len(agent_data["tools_executed"]) > 0
    print(f"[PASS] /api/v1/agent/chat (Tool executed: {agent_data['tools_executed'][0]['name']}, Model: {agent_data['model_used']})")

    # 8. Recommendation Feedback Loop
    fb_res = client.post("/api/v1/feedback/", json={
        "opportunity_id": opp_id,
        "feedback_type": "relevant",
        "notes": "Strong match for Python distributed systems."
    }, headers=headers)
    assert fb_res.status_code == 200
    print("[PASS] /api/v1/feedback/")

    # 9. Dashboard Analytics
    dash_res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    print("Dash active opps:", dash_data["total_active_opportunities"])
    assert dash_data["total_active_opportunities"] >= 10
    print(f"[PASS] /api/v1/analytics/dashboard (Active: {dash_data['total_active_opportunities']}, Avg Compat: {dash_data['average_compatibility']}%)")

    # 10. Evaluation Runs
    eval_res = client.get("/api/v1/evaluation/runs")
    assert eval_res.status_code == 200
    runs = eval_res.json()
    assert len(runs) >= 4
    print(f"[PASS] /api/v1/evaluation/runs ({len(runs)} benchmark runs verified: MRR={runs[0]['mrr']}, NDCG@5={runs[0]['ndcg_at_k'].get('k=5')})")

    print("\nALL BACKEND SMOKE TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    run_smoke_test()
