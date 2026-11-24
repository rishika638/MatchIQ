"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { 
  Search, SlidersHorizontal, Sparkles, Filter, Bookmark, BookmarkCheck, 
  Layers, CheckCircle2, XCircle, ArrowUpRight, ChevronRight, Zap, RefreshCw 
} from "lucide-react";
import { api } from "@/lib/api";
import { SearchResponse, SearchResultItem } from "@/types";

function DiscoverContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [enableReranking, setEnableReranking] = useState(false);
  const [workMode, setWorkMode] = useState<string>("");
  const [oppType, setOppType] = useState<string>("");
  const [minSalary, setMinSalary] = useState<number>(0);
  const [selectedSkill, setSelectedSkill] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [savingId, setSavingId] = useState<string | null>(null);

  const fetchResults = async (qText = query, rerank = enableReranking) => {
    setLoading(true);
    try {
      const filters: any = {};
      if (workMode) filters.work_modes = [workMode];
      if (oppType) filters.opportunity_types = [oppType];
      if (minSalary > 0) filters.min_salary = minSalary;
      if (selectedSkill) filters.skills = [selectedSkill];

      const res = await api.search({
        query: qText,
        ...filters,
        enable_reranking: rerank,
        page: 1,
        page_size: 20
      });
      setSearchResponse(res);
    } catch (err: any) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults(initialQuery, enableReranking);

    // Load saved IDs if user is logged in
    api.getSavedOpportunities().then((saved) => {
      if (Array.isArray(saved)) {
        setSavedIds(new Set(saved.map((s: any) => s.opportunity_id)));
      }
    }).catch(() => {});
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchResults();
  };

  const toggleSave = async (oppId: string) => {
    setSavingId(oppId);
    try {
      if (savedIds.has(oppId)) {
        await api.removeSaved(oppId);
        setSavedIds((prev) => {
          const next = new Set(prev);
          next.delete(oppId);
          return next;
        });
      } else {
        await api.saveOpportunity({ opportunity_id: oppId, status: "saved" });
        setSavedIds((prev) => new Set(prev).add(oppId));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header & Search Bar */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Opportunity Discovery</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Hybrid dense-vector & lexical search engine powered by Reciprocal Rank Fusion and Cross-Encoder reranking.
        </p>

        <form onSubmit={handleSearchSubmit} className="mt-6 flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Senior Distributed Systems engineer with Go, Kubernetes and Kafka..."
              className="w-full bg-navy-900 border border-navy-700/80 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition shadow-inner"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition shadow-md shadow-brand-500/20 disabled:opacity-50"
          >
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Execute Retrieval
          </button>
        </form>

        {/* Filters and Reranking Toggle Bar */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-navy-900/60 border border-navy-800 text-xs text-slate-300">
          <div className="flex flex-wrap items-center gap-3">
            <span className="flex items-center gap-1 text-slate-400 font-medium">
              <Filter className="h-3.5 w-3.5" /> Filters:
            </span>

            {/* Work Mode */}
            <select
              value={workMode}
              onChange={(e) => { setWorkMode(e.target.value); }}
              className="bg-navy-950 border border-navy-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none"
            >
              <option value="">Work Mode (All)</option>
              <option value="remote">Remote Only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite</option>
            </select>

            {/* Opportunity Type */}
            <select
              value={oppType}
              onChange={(e) => { setOppType(e.target.value); }}
              className="bg-navy-950 border border-navy-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none"
            >
              <option value="">Opportunity Type (All)</option>
              <option value="full-time">Full-time</option>
              <option value="internship">Internship</option>
              <option value="contract">Contract</option>
            </select>

            {/* Skill Quick Filter */}
            <select
              value={selectedSkill}
              onChange={(e) => { setSelectedSkill(e.target.value); }}
              className="bg-navy-950 border border-navy-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none"
            >
              <option value="">Specific Skill</option>
              <option value="Python">Python</option>
              <option value="Go">Go / Golang</option>
              <option value="Rust">Rust</option>
              <option value="Kubernetes">Kubernetes</option>
              <option value="PyTorch">PyTorch / AI</option>
              <option value="TypeScript">TypeScript</option>
              <option value="Kafka">Kafka</option>
            </select>
          </div>

          {/* Cross-Encoder Reranking Toggle */}
          <div className="flex items-center gap-2.5">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={enableReranking}
                onChange={(e) => {
                  setEnableReranking(e.target.checked);
                  fetchResults(query, e.target.checked);
                }}
                className="h-3.5 w-3.5 rounded border-navy-700 bg-navy-950 text-brand-500 focus:ring-0"
              />
              <span className="text-xs font-semibold text-brand-300 flex items-center gap-1">
                <Sparkles className="h-3 w-3 text-brand-400" />
                Cross-Encoder Reranking
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Latency & Method Metadata */}
      {searchResponse && (
        <div className="mb-4 flex flex-wrap items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2 font-mono text-[11px]">
            <span>Matches: <strong className="text-white">{searchResponse.total_matches}</strong></span>
            <span>•</span>
            <span>Pipeline: <strong className="text-indigo-400">{searchResponse.retrieval_method}</strong></span>
            <span>•</span>
            <span>Latency: <strong className="text-emerald-400">{searchResponse.latency_ms} ms</strong></span>
          </div>
          <span className="text-[11px]">Ranked via Reciprocal Rank Fusion (k=60)</span>
        </div>
      )}

      {/* Results List */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Running vector similarity & full-text lexical fusion...</span>
        </div>
      ) : searchResponse && searchResponse.results.length > 0 ? (
        <div className="space-y-4">
          {searchResponse.results.map((item) => {
            const opp = item.opportunity;
            const meta = item.retrieval_meta;
            const compat = item.compatibility;
            const isSaved = savedIds.has(opp.id);

            return (
              <div
                key={opp.id}
                className="p-5 rounded-2xl bg-navy-900/70 border border-navy-800/80 hover:border-navy-700 transition flex flex-col justify-between gap-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 rounded bg-navy-800 text-brand-300 font-mono text-[10px]">
                        {opp.id}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-medium text-[11px] border border-indigo-500/20 capitalize">
                        {opp.opportunity_type}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] capitalize">
                        {opp.work_mode}
                      </span>
                    </div>

                    <h2 className="text-lg font-bold text-white hover:text-brand-300 transition">
                      <Link href={`/opportunities/${opp.id}`}>{opp.title}</Link>
                    </h2>
                    <p className="text-xs font-semibold text-slate-300">
                      {opp.company} • <span className="text-slate-400 font-normal">{opp.location}</span>
                    </p>
                  </div>

                  {/* Compatibility & Action */}
                  <div className="flex items-center gap-3 sm:flex-col sm:items-end">
                    {compat && (
                      <div className="flex items-center gap-2">
                        <div className="text-right">
                          <span className="block text-xs font-bold text-white">
                            {compat.overall_compatibility}% Match
                          </span>
                          <span className="block text-[10px] text-slate-400">
                            Semantic & Skills
                          </span>
                        </div>
                        <div className="h-9 w-9 rounded-full bg-brand-600/20 border border-brand-500/40 flex items-center justify-center font-bold text-xs text-brand-300 font-mono">
                          {Math.round(compat.overall_compatibility)}
                        </div>
                      </div>
                    )}

                    <button
                      onClick={() => toggleSave(opp.id)}
                      disabled={savingId === opp.id}
                      className={`p-2 rounded-xl border text-xs transition flex items-center gap-1.5 ${
                        isSaved
                          ? "bg-brand-600/20 border-brand-500/40 text-brand-300"
                          : "bg-navy-950 border-navy-800 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {isSaved ? <BookmarkCheck className="h-4 w-4 text-brand-400" /> : <Bookmark className="h-4 w-4" />}
                      <span className="hidden sm:inline">{isSaved ? "Saved" : "Save"}</span>
                    </button>
                  </div>
                </div>

                {/* Description Excerpt */}
                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                  {opp.description}
                </p>

                {/* Skills tags */}
                <div className="flex flex-wrap items-center gap-1.5 pt-2">
                  <span className="text-[11px] text-slate-500 font-medium mr-1">Required:</span>
                  {opp.required_skills.map((skill) => {
                    const isMatched = compat?.matching_skills.includes(skill);
                    return (
                      <span
                        key={skill}
                        className={`px-2 py-0.5 rounded text-[10px] font-medium transition ${
                          isMatched
                            ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/25"
                            : "bg-navy-950 text-slate-300 border border-navy-800"
                        }`}
                      >
                        {skill}
                      </span>
                    );
                  })}
                </div>

                {/* Retrieval Breakdown Diagnostics Bar */}
                <div className="pt-3 border-t border-navy-800/80 flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-400 font-mono">
                  <div className="flex flex-wrap items-center gap-3">
                    <span>RRF: <strong className="text-slate-200">{meta.rrf_score}</strong></span>
                    <span>Cosine: <strong className="text-slate-200">{meta.semantic_score}</strong></span>
                    {meta.reranker_score !== null && (
                      <span>Reranker: <strong className="text-brand-300">{meta.reranker_score}</strong></span>
                    )}
                    <span>Comp: <strong className="text-slate-200">${opp.min_salary.toLocaleString()} - ${opp.max_salary.toLocaleString()}</strong></span>
                  </div>

                  <Link
                    href={`/opportunities/${opp.id}`}
                    className="text-brand-400 hover:text-brand-300 font-semibold font-sans flex items-center gap-1"
                  >
                    View Details & Explanations <ChevronRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-20 text-center bg-navy-900/40 border border-navy-800 rounded-2xl p-8">
          <p className="text-sm text-slate-400">No active opportunities matched the specified hybrid query and filters.</p>
          <button
            onClick={() => { setQuery(""); setWorkMode(""); setOppType(""); setSelectedSkill(""); fetchResults("", enableReranking); }}
            className="mt-4 px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-700 text-slate-200 text-xs font-semibold"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
}

export default function DiscoverPage() {
  return (
    <Suspense fallback={<div className="py-20 text-center text-xs text-slate-400">Loading opportunity discovery...</div>}>
      <DiscoverContent />
    </Suspense>
  );
}
