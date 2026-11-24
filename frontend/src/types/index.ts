export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  organization_id?: string;
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  headline: string;
  bio: string;
  experience_years: number;
  skills: string[];
  preferred_locations: string[];
  preferred_work_modes: string[];
  preferred_opportunity_types: string[];
  preferred_min_salary: number;
  preferred_currency: string;
  preferred_roles: string[];
  education: Array<{ degree: string; field: string; year?: string }>;
  experience_records: Array<{ title: string; duration: string; description: string }>;
  projects: Array<{ name: string; description: string }>;
  resume_filename?: string;
  updated_at?: string;
}

export interface Opportunity {
  id: string;
  title: string;
  company: string;
  department?: string;
  location: string;
  work_mode: string;
  opportunity_type: string;
  experience_level: string;
  min_years_experience: number;
  max_years_experience: number;
  min_salary: number;
  max_salary: number;
  currency: string;
  description: string;
  responsibilities: string[];
  benefits: string[];
  required_skills: string[];
  nice_to_have_skills: string[];
  is_synthetic: boolean;
  source: string;
  application_url?: string;
  contact_email?: string;
  created_at?: string;
}

export interface CompatibilityAnalysis {
  overall_compatibility: number;
  components: {
    semantic_similarity: number;
    skills_overlap: number;
    experience_compatibility: number;
    role_relevance: number;
    preference_compatibility: number;
  };
  weights_used: Record<string, number>;
  matching_skills: string[];
  missing_skills: string[];
  nice_to_have_missing: string[];
  eligibility: {
    is_eligible: boolean;
    violations: string[];
    status: string;
  };
  explanation: string;
  methodology_notice: string;
}

export interface SearchResultItem {
  opportunity: Opportunity;
  retrieval_meta: {
    rrf_score: number;
    semantic_score: number;
    keyword_score: number;
    reranker_score: number | null;
    final_score: number;
    cross_encoder_applied: boolean;
  };
  compatibility?: CompatibilityAnalysis | null;
}

export interface SearchResponse {
  query: string;
  retrieval_method: string;
  total_matches: number;
  page: number;
  page_size: number;
  total_pages: number;
  latency_ms: number;
  results: SearchResultItem[];
}

export interface SavedOpportunityItem {
  id: string;
  opportunity_id: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  opportunity: Opportunity;
  compatibility?: CompatibilityAnalysis | null;
}

export interface DashboardMetrics {
  total_active_opportunities: number;
  saved_opportunities: number;
  applied_opportunities: number;
  average_compatibility: number;
  top_missing_skills: Array<{ skill: string; demand_count: number }>;
  top_matching_skills: Array<{ skill: string; frequency: number }>;
  work_mode_distribution: Record<string, number>;
  feedback_summary: Record<string, number>;
  recent_searches: Array<{
    query: string;
    retrieval_method: string;
    result_count: number;
    latency_ms: number;
    created_at: string;
  }>;
}

export interface EvaluationRun {
  id: string;
  dataset_version: string;
  retrieval_method: string;
  embedding_model: string;
  reranker_model?: string;
  precision_at_k: Record<string, number>;
  recall_at_k: Record<string, number>;
  mrr: number;
  ndcg_at_k: Record<string, number>;
  average_latency_ms: number;
  detailed_metrics?: any;
  created_at: string;
}

export interface AgentChatMessage {
  id?: string;
  sender: "user" | "assistant" | "system";
  content: string;
  tool_calls?: any[];
  tool_results?: any[];
  model?: string;
  created_at?: string;
}
