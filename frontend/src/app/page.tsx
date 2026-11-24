"use client";

import React from "react";
import Link from "next/link";
import { 
  Sparkles, Search, Bot, BarChart3, ShieldCheck, Cpu, 
  ArrowRight, CheckCircle2, Layers, Compass, FileText, Zap 
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center">
      {/* Hero Section */}
      <section className="relative w-full pt-20 pb-24 overflow-hidden border-b border-navy-800/50">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(99,102,241,0.15),rgba(255,255,255,0))] pointer-events-none" />
        
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-brand-500/30 bg-brand-500/10 text-brand-300 text-xs font-medium mb-6">
            <Sparkles className="h-3.5 w-3.5 text-brand-400" />
            <span>MatchIQ 2.0 • Hybrid Vector & Keyword Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight sm:leading-none">
            The AI Opportunity <span className="bg-gradient-to-r from-brand-300 via-indigo-300 to-indigo-500 bg-clip-text text-transparent">Intelligence Engine</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Move beyond superficial keyword filters. MatchIQ delivers transparent, semantic career intelligence with pgvector retrieval, Reciprocal Rank Fusion, explainable scoring, and an autonomous AI career copilot.
          </p>

          {/* Interactive Query Box Demo */}
          <div className="mt-10 max-w-3xl mx-auto bg-navy-900/90 border border-navy-700/80 rounded-2xl p-2 shadow-2xl shadow-navy-950/80">
            <div className="flex items-center gap-3 px-4 py-3 bg-navy-950/60 rounded-xl border border-navy-800/80">
              <Search className="h-5 w-5 text-brand-400 flex-shrink-0" />
              <input 
                type="text" 
                readOnly
                value="I want a backend engineering internship involving Python, distributed systems and AI."
                className="w-full bg-transparent text-sm sm:text-base text-slate-200 outline-none select-none cursor-default font-mono"
              />
              <Link
                href="/discover?q=I%20want%20a%20backend%20engineering%20internship%20involving%20Python,%20distributed%20systems%20and%20AI"
                className="flex items-center gap-1.5 text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white px-4 py-2.5 rounded-lg transition whitespace-nowrap shadow-md shadow-brand-500/25"
              >
                Run Search
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5 text-indigo-400" />
                Dense 384-D Vector + PostgreSQL FTS + RRF (k=60)
              </span>
              <span className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                100 Verified Tech Roles Ingested
              </span>
            </div>
          </div>

          {/* Quick CTA Buttons */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm transition shadow-lg shadow-brand-600/25 flex items-center gap-2"
            >
              Open Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/agent"
              className="px-6 py-3 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-200 font-semibold text-sm transition border border-navy-700/80 flex items-center gap-2"
            >
              <Bot className="h-4 w-4 text-brand-400" />
              Launch Career Copilot
            </Link>
            <Link
              href="/evaluation"
              className="px-6 py-3 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-200 font-semibold text-sm transition border border-navy-700/80 flex items-center gap-2"
            >
              <BarChart3 className="h-4 w-4 text-emerald-400" />
              View Benchmark Runs
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Pillar Grid */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
        <div className="text-center mb-16">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Engineered for Ground-Truth Career Decisions
          </h2>
          <p className="mt-3 text-slate-400 text-sm max-w-xl mx-auto">
            Transparent scoring heuristics, multi-stage retrieval, and zero simulated responses.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="rounded-2xl border border-navy-800 bg-navy-900/60 p-6 flex flex-col justify-between hover:border-navy-700 transition">
            <div>
              <div className="h-10 w-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 mb-4">
                <Layers className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-white">Hybrid Retrieval & RRF</h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                Fuses pgvector cosine distance with PostgreSQL full-text keyword search via Reciprocal Rank Fusion. Optional cross-encoder reranking provides precision attention scoring.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-navy-800 text-xs text-brand-300 font-mono">
              k = 60 • MRR & NDCG Evaluated
            </div>
          </div>

          {/* Card 2 */}
          <div className="rounded-2xl border border-navy-800 bg-navy-900/60 p-6 flex flex-col justify-between hover:border-navy-700 transition">
            <div>
              <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-white">Explainable Matching Engine</h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                No black-box guesses. Clearly displays semantic alignment, skill overlap ratios, experience tenure compatibility, and separates hard eligibility constraints from relevance rankings.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-navy-800 text-xs text-indigo-300 font-mono">
              Transparent Scoring Breakdown
            </div>
          </div>

          {/* Card 3 */}
          <div className="rounded-2xl border border-navy-800 bg-navy-900/60 p-6 flex flex-col justify-between hover:border-navy-700 transition">
            <div>
              <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
                <Bot className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-white">AI Career Copilot Agent</h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                Autonomous agent with real backend tool execution: search opportunities, analyze skill gaps, save to tracker, and update preferences with persistent PostgreSQL memory.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-navy-800 text-xs text-emerald-300 font-mono">
              Gemini + Deterministic Engine
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
