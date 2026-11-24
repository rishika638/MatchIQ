const configuredApiBase = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, "");
const API_BASE = configuredApiBase || "http://localhost:8000/api/v1";

class ApiClient {
  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("matchiq_token");
    }
    return null;
  }

  public setToken(token: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("matchiq_token", token);
    }
  }

  public clearToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("matchiq_token");
      localStorage.removeItem("matchiq_user");
    }
  }

  public getUser(): any | null {
    if (typeof window !== "undefined") {
      const u = localStorage.getItem("matchiq_user");
      return u ? JSON.parse(u) : null;
    }
    return null;
  }

  public setUser(user: any) {
    if (typeof window !== "undefined") {
      localStorage.setItem("matchiq_user", JSON.stringify(user));
    }
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    if (process.env.NODE_ENV === "production" && !configuredApiBase) {
      throw new Error("NEXT_PUBLIC_API_URL is required in production.");
    }
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      let errorDetail = "API Error";
      try {
        const errorData = await res.json();
        errorDetail = errorData.detail || errorData.message || JSON.stringify(errorData);
      } catch {
        errorDetail = res.statusText;
      }
      throw new Error(errorDetail);
    }

    return res.json() as Promise<T>;
  }

  // Auth
  async login(payload: any) {
    return this.request<{ access_token: string; user: any }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async register(payload: any) {
    return this.request<{ access_token: string; user: any }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getMe() {
    return this.request<any>("/auth/me");
  }

  // Candidates
  async getProfile() {
    return this.request<any>("/candidates/profile");
  }

  async updateProfile(payload: any) {
    return this.request<any>("/candidates/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  async uploadResume(formData: FormData) {
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${API_BASE}/candidates/resume/upload`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  }

  // Search
  async search(payload: any) {
    return this.request<any>("/search/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Opportunities
  async getOpportunity(id: string) {
    return this.request<any>(`/opportunities/${id}`);
  }

  async listOpportunities(params: string = "") {
    return this.request<any>(`/opportunities/${params}`);
  }

  async compareOpportunities(opportunityIds: string[]) {
    return this.request<any>("/opportunities/compare", {
      method: "POST",
      body: JSON.stringify({ opportunity_ids: opportunityIds }),
    });
  }

  // Saved Opportunities
  async getSavedOpportunities(status?: string) {
    const q = status ? `?status_filter=${status}` : "";
    return this.request<any[]>(`/saved/${q}`);
  }

  async saveOpportunity(payload: { opportunity_id: string; status?: string; notes?: string }) {
    return this.request<any>("/saved/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async updateSavedStatus(opportunityId: string, payload: { status?: string; notes?: string }) {
    return this.request<any>(`/saved/${opportunityId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  }

  async removeSaved(opportunityId: string) {
    return this.request<any>(`/saved/${opportunityId}`, {
      method: "DELETE",
    });
  }

  // Feedback
  async submitFeedback(payload: { opportunity_id: string; feedback_type: string; notes?: string; query_or_context?: string }) {
    return this.request<any>("/feedback/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getFeedbackAnalytics() {
    return this.request<any>("/feedback/analytics");
  }

  // Agent Chat
  async chatWithAgent(message: string, conversationId?: string) {
    return this.request<any>("/agent/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  async getConversations() {
    return this.request<any[]>("/agent/conversations");
  }

  async getConversationMessages(convoId: string) {
    return this.request<any>(`/agent/conversations/${convoId}/messages`);
  }

  // Evaluation & Benchmarking
  async getBenchmarkQueries() {
    return this.request<any[]>("/evaluation/benchmark-queries");
  }

  async getEvaluationRuns() {
    return this.request<any[]>("/evaluation/runs");
  }

  async runFullEvaluation() {
    return this.request<any>("/evaluation/run-suite", {
      method: "POST",
    });
  }

  async runMethodEvaluation(method: string) {
    return this.request<any>(`/evaluation/run/${method}`, {
      method: "POST",
    });
  }

  // Dashboard & Ingestion
  async getDashboardMetrics() {
    return this.request<any>("/analytics/dashboard");
  }

  async reindexEmbeddings() {
    return this.request<any>("/ingestion/reindex", {
      method: "POST",
    });
  }
}

export const api = new ApiClient();
