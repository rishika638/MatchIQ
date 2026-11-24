"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { 
  Building2, MapPin, DollarSign, Calendar, Clock, Bookmark, 
  BookmarkCheck, CheckCircle2, XCircle, AlertTriangle, Sparkles, 
  Bot, ArrowLeft, ThumbsUp, ThumbsDown, Check, Send, ExternalLink 
} from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";
import { api } from "@/lib/api";
import { Opportunity, CompatibilityAnalysis } from "@/types";

export default function OpportunityDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [opp, setOpp] = useState<Opportunity | null>(null);
  const [compat, setCompat] = useState<CompatibilityAnalysis | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [feedbackRecorded, setFeedbackRecorded] = useState<string | null>(null);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await api.getOpportunity(id);
        setOpp(data.opportunity);
        setCompat(data.compatibility);
        setIsSaved(Boolean(data.user_saved_status));
      } catch (err) {
        console.error("Failed to load opportunity:", err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadData();
  }, [id]);

  const handleToggleSave = async () => {
    if (!opp) return;
    try {
      if (isSaved) {
        await api.removeSaved(opp.id);
        setIsSaved(false);
      } else {
        await api.saveOpportunity({ opportunity_id: opp.id, status: "saved", notes });
        setIsSaved(true);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFeedback = async (type: string) => {
    if (!opp) return;
    try {
      await api.submitFeedback({
        opportunity_id: opp.id,
        feedback_type: type,
        notes: `User rated ${type} on detail view.`
      });
      setFeedbackRecorded(type);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Loading opportunity intelligence breakdown...</span>
        </div>
      </div>
    );
  }

  if (!opp) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-bold text-white">Opportunity not found</h2>
        <Link href="/discover" className="mt-4 inline-block text-xs text-brand-400 underline">
          Return to Opportunity Discovery
        </Link>
      </div>
    );
  }

  const componentChartData = compat ? [
    { name: "Semantic", score: compat.components.semantic_similarity },
    { name: "Skills Overlap", score: compat.components.skills_overlap },
    { name: "Experience", score: compat.components.experience_compatibility },
    { name: "Role Relevance", score: compat.components.role_relevance },
    { name: "Preferences", score: compat.components.preference_compatibility }
  ] : [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Back button */}
      <Link
        href="/discover"
        className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Opportunity Discovery
      </Link>

      {/* Main Role Header */}
      <div className="p-6 sm:p-8 rounded-2xl bg-navy-900/90 border border-navy-800 mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded bg-brand-500/10 text-brand-300 font-mono text-xs border border-brand-500/20">
                {opp.id}
              </span>
              <span className="px-2.5 py-0.5 rounded bg-navy-800 text-slate-300 text-xs capitalize">
                {opp.opportunity_type}
              </span>
              <span className="px-2.5 py-0.5 rounded bg-navy-800 text-slate-300 text-xs capitalize">
                {opp.work_mode}
              </span>
              {opp.is_synthetic && (
                <span className="px-2 py-0.5 rounded bg-navy-800/80 text-slate-400 text-[10px] font-mono">
                  Synthetic Demo Record
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {opp.title}
            </h1>
            <p className="mt-1 text-sm font-semibold text-slate-300 flex items-center gap-2">
              <Building2 className="h-4 w-4 text-brand-400" />
              {opp.company} • <span className="text-slate-400 font-normal">{opp.location}</span>
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleToggleSave}
              className={`px-4 py-2.5 rounded-xl border text-xs font-semibold transition flex items-center gap-2 ${
                isSaved
                  ? "bg-brand-600/20 border-brand-500/40 text-brand-300"
                  : "bg-navy-950 border-navy-700 text-slate-200 hover:bg-navy-850"
              }`}
            >
              {isSaved ? <BookmarkCheck className="h-4 w-4 text-brand-400" /> : <Bookmark className="h-4 w-4" />}
              {isSaved ? "Saved in Tracker" : "Save Opportunity"}
            </button>

            <Link
              href={`/agent?msg=Analyze%20skill%20gaps%20and%20interview%20prep%20for%20${opp.id}`}
              className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition flex items-center gap-2 shadow-md shadow-brand-500/20"
            >
              <Bot className="h-4 w-4" />
              Ask Copilot
            </Link>
          </div>
        </div>

        {/* Quick Highlights Grid */}
        <div className="mt-6 pt-6 border-t border-navy-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block">Annual Compensation</span>
            <span className="font-semibold text-slate-200 mt-0.5 block">
              ${opp.min_salary.toLocaleString()} - ${opp.max_salary.toLocaleString()} {opp.currency}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Experience Required</span>
            <span className="font-semibold text-slate-200 mt-0.5 block">
              {opp.min_years_experience} - {opp.max_years_experience} years
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Experience Level</span>
            <span className="font-semibold text-slate-200 mt-0.5 block capitalize">
              {opp.experience_level}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Department</span>
            <span className="font-semibold text-slate-200 mt-0.5 block">
              {opp.department || "Core Engineering"}
            </span>
          </div>
        </div>
      </div>

      {/* Explainable Matching Engine Section */}
      {compat && (
        <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-navy-900 via-navy-900/90 to-brand-950/40 border border-brand-500/30 mb-8 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-brand-500/10 text-brand-300 text-xs font-semibold border border-brand-500/20 mb-1.5">
                <Sparkles className="h-3.5 w-3.5 text-brand-400" />
                Explainable Matching Engine
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">Candidate Compatibility Breakdown</h2>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-2xl font-black text-white font-mono">{compat.overall_compatibility}%</span>
                <span className="text-[10px] text-slate-400 block">Overall Alignment</span>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-brand-600/30 border border-brand-500/50 flex items-center justify-center font-bold text-brand-300 text-lg font-mono">
                {Math.round(compat.overall_compatibility)}
              </div>
            </div>
          </div>

          {/* Explanation narrative */}
          <div className="p-4 rounded-xl bg-navy-950/80 border border-navy-800 text-xs text-slate-300 leading-relaxed mb-6">
            <strong>Why this matched:</strong> {compat.explanation}
          </div>

          {/* Component Bar Chart & Skills Overlap Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Component breakdown */}
            <div className="p-4 rounded-xl bg-navy-950/60 border border-navy-800">
              <h3 className="text-xs font-bold text-white mb-3">Scoring Component Weights</h3>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={componentChartData} layout="vertical" margin={{ left: 10, right: 10, top: 0, bottom: 0 }}>
                    <XAxis type="number" domain={[0, 100]} stroke="#64748b" fontSize={10} />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} width={90} />
                    <Tooltip contentStyle={{ backgroundColor: "#0b1120", borderColor: "#1e293b", fontSize: "11px" }} />
                    <Bar dataKey="score" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Skills Matched vs Missing */}
            <div className="p-4 rounded-xl bg-navy-950/60 border border-navy-800 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-bold text-white mb-2">Required Skills Overlap</h3>
                
                <div className="space-y-3">
                  <div>
                    <span className="text-[11px] text-emerald-400 font-semibold block mb-1">
                      ✓ Matching Skills ({compat.matching_skills.length})
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {compat.matching_skills.map((s) => (
                        <span key={s} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px]">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-[11px] text-rose-400 font-semibold block mb-1">
                      ✕ Skill Gaps to Bridge ({compat.missing_skills.length})
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {compat.missing_skills.length > 0 ? (
                        compat.missing_skills.map((s) => (
                          <span key={s} className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[10px]">
                            {s}
                          </span>
                        ))
                      ) : (
                        <span className="text-[10px] text-slate-500">None! You possess all required skills.</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Hard Eligibility status */}
              <div className="mt-4 pt-3 border-t border-navy-800 text-[11px] flex items-center justify-between">
                <span className="text-slate-400">Eligibility Status:</span>
                <span className={`font-semibold flex items-center gap-1 ${
                  compat.eligibility.is_eligible ? "text-emerald-400" : "text-amber-400"
                }`}>
                  {compat.eligibility.is_eligible ? <CheckCircle2 className="h-3.5 w-3.5" /> : <AlertTriangle className="h-3.5 w-3.5" />}
                  {compat.eligibility.status}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Two Column Layout: Description & Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Left Column: Job Description and Responsibilities */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
            <h2 className="text-sm font-bold text-white mb-3">About the Role</h2>
            <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
              {opp.description}
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
            <h2 className="text-sm font-bold text-white mb-3">Key Responsibilities</h2>
            <ul className="space-y-2 text-xs text-slate-300">
              {opp.responsibilities.map((resp, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-brand-400 mt-0.5">•</span>
                  <span>{resp}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
            <h2 className="text-sm font-bold text-white mb-3">Benefits & Perks</h2>
            <ul className="space-y-2 text-xs text-slate-300">
              {opp.benefits.map((b, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-emerald-400 mt-0.5">✓</span>
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right Column: Skills, Feedback Loop & Application */}
        <div className="space-y-6">
          {/* Recommendation Feedback Loop */}
          <div className="p-5 rounded-2xl bg-navy-900/60 border border-navy-800">
            <h3 className="text-xs font-bold text-white mb-1.5">Recommendation Feedback Loop</h3>
            <p className="text-[11px] text-slate-400 mb-3">
              Help calibrate the intelligence engine. How well does this role fit your career goals?
            </p>

            {feedbackRecorded ? (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                <Check className="h-4 w-4" />
                <span>Feedback recorded as: <strong>{feedbackRecorded}</strong></span>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  onClick={() => handleFeedback("relevant")}
                  className="p-2 rounded-lg bg-navy-950 border border-navy-800 hover:border-emerald-500/50 hover:bg-emerald-500/10 text-slate-200 transition flex items-center justify-center gap-1.5"
                >
                  <ThumbsUp className="h-3.5 w-3.5 text-emerald-400" />
                  Relevant
                </button>
                <button
                  onClick={() => handleFeedback("not_relevant")}
                  className="p-2 rounded-lg bg-navy-950 border border-navy-800 hover:border-rose-500/50 hover:bg-rose-500/10 text-slate-200 transition flex items-center justify-center gap-1.5"
                >
                  <ThumbsDown className="h-3.5 w-3.5 text-rose-400" />
                  Not Relevant
                </button>
                <button
                  onClick={() => handleFeedback("applied")}
                  className="p-2 rounded-lg bg-navy-950 border border-navy-800 hover:border-brand-500/50 hover:bg-brand-500/10 text-slate-200 transition flex items-center justify-center gap-1.5"
                >
                  <CheckCircle2 className="h-3.5 w-3.5 text-brand-400" />
                  Applied
                </button>
                <button
                  onClick={() => handleFeedback("not_interested")}
                  className="p-2 rounded-lg bg-navy-950 border border-navy-800 hover:border-slate-600 text-slate-400 transition flex items-center justify-center gap-1.5"
                >
                  <XCircle className="h-3.5 w-3.5" />
                  Not Interested
                </button>
              </div>
            )}
          </div>

          {/* Quick Apply / Tracker Notes */}
          <div className="p-5 rounded-2xl bg-navy-900/60 border border-navy-800">
            <h3 className="text-xs font-bold text-white mb-2">Application Tracker Notes</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Private notes (e.g. referral contact, interview dates)..."
              rows={3}
              className="w-full bg-navy-950 border border-navy-800 rounded-xl p-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
            />
            <button
              onClick={handleToggleSave}
              className="mt-2 w-full py-2 bg-navy-800 hover:bg-navy-700 text-slate-200 text-xs font-semibold rounded-lg transition"
            >
              Update Tracker Notes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
