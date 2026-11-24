"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Building2, MapPin, DollarSign, CheckCircle2, XCircle, 
  AlertTriangle, ArrowLeft, Plus, Trash2, Sparkles, RefreshCw 
} from "lucide-react";
import { api } from "@/lib/api";
import { Opportunity, CompatibilityAnalysis } from "@/types";

export default function ComparePage() {
  const [availableOpps, setAvailableOpps] = useState<Opportunity[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>(["opp-seed-001", "opp-seed-002"]);
  const [comparisons, setComparisons] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load opportunity choices
    api.listOpportunities("?limit=50").then((res) => {
      if (res && res.items) setAvailableOpps(res.items);
    }).catch(() => {});
  }, []);

  const runComparison = async (ids = selectedIds) => {
    if (ids.length < 2) return;
    setLoading(true);
    try {
      const res = await api.compareOpportunities(ids);
      setComparisons(res.results || []);
    } catch (err) {
      console.error("Comparison failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runComparison(selectedIds);
  }, [selectedIds]);

  const addOppToCompare = (idToAdd: string) => {
    if (idToAdd && !selectedIds.includes(idToAdd) && selectedIds.length < 4) {
      setSelectedIds([...selectedIds, idToAdd]);
    }
  };

  const removeOppFromCompare = (idToRemove: string) => {
    if (selectedIds.length > 2) {
      setSelectedIds(selectedIds.filter((id) => id !== idToRemove));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Opportunity Comparison Matrix</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Compare 2 to 4 technical roles side by side across compensation, skills overlap, and compatibility.
          </p>
        </div>

        {/* Add selector */}
        {selectedIds.length < 4 && (
          <div className="flex items-center gap-2">
            <select
              onChange={(e) => {
                if (e.target.value) {
                  addOppToCompare(e.target.value);
                  e.target.value = "";
                }
              }}
              defaultValue=""
              className="bg-navy-900 border border-navy-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none"
            >
              <option value="" disabled>+ Add Role to Compare</option>
              {availableOpps
                .filter((o) => !selectedIds.includes(o.id))
                .map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.title} — {o.company}
                  </option>
                ))}
            </select>
          </div>
        )}
      </div>

      {/* Comparison Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Running side-by-side compatibility matrix...</span>
        </div>
      ) : comparisons.length >= 2 ? (
        <div className="overflow-x-auto pb-4">
          <div className={`grid gap-4 min-w-[700px]`} style={{ gridTemplateColumns: `repeat(${comparisons.length}, minmax(280px, 1fr))` }}>
            {comparisons.map((c, idx) => {
              const opp: Opportunity = c.opportunity;
              const compat: CompatibilityAnalysis = c.compatibility;

              return (
                <div
                  key={opp.id}
                  className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 flex flex-col justify-between gap-6"
                >
                  {/* Header */}
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-[10px] font-mono text-brand-300 px-2 py-0.5 rounded bg-navy-950 border border-navy-800">
                        {opp.id}
                      </span>
                      {selectedIds.length > 2 && (
                        <button
                          onClick={() => removeOppFromCompare(opp.id)}
                          className="text-slate-500 hover:text-rose-400 transition"
                          title="Remove from comparison"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>

                    <h2 className="text-lg font-bold text-white leading-snug">
                      <Link href={`/opportunities/${opp.id}`} className="hover:text-brand-300 transition">
                        {opp.title}
                      </Link>
                    </h2>
                    <p className="text-xs font-semibold text-slate-300 mt-1">
                      {opp.company} • <span className="text-slate-400 font-normal">{opp.location}</span>
                    </p>
                  </div>

                  {/* Compatibility score pill */}
                  {compat && (
                    <div className="p-3 rounded-xl bg-navy-950/80 border border-brand-500/20 flex items-center justify-between">
                      <div>
                        <span className="text-[10px] text-slate-400 block">Candidate Fit</span>
                        <span className="text-lg font-black text-white font-mono">
                          {compat.overall_compatibility}%
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] text-slate-400 block">Status</span>
                        <span className={`text-xs font-semibold ${compat.eligibility.is_eligible ? "text-emerald-400" : "text-amber-400"}`}>
                          {compat.eligibility.status}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Attribute list */}
                  <div className="space-y-3 text-xs divide-y divide-navy-800/80">
                    <div className="pt-2 flex justify-between">
                      <span className="text-slate-400">Compensation:</span>
                      <span className="font-semibold text-slate-200">
                        ${opp.min_salary.toLocaleString()} - ${opp.max_salary.toLocaleString()}
                      </span>
                    </div>

                    <div className="pt-2 flex justify-between">
                      <span className="text-slate-400">Tenure Requirement:</span>
                      <span className="font-semibold text-slate-200">
                        {opp.min_years_experience} - {opp.max_years_experience} yrs
                      </span>
                    </div>

                    <div className="pt-2 flex justify-between">
                      <span className="text-slate-400">Work Mode:</span>
                      <span className="font-semibold text-slate-200 capitalize">
                        {opp.work_mode}
                      </span>
                    </div>

                    <div className="pt-2 flex justify-between">
                      <span className="text-slate-400">Opportunity Type:</span>
                      <span className="font-semibold text-slate-200 capitalize">
                        {opp.opportunity_type}
                      </span>
                    </div>
                  </div>

                  {/* Skills Section */}
                  <div>
                    <span className="text-[11px] text-slate-400 font-semibold block mb-1.5">Required Skills:</span>
                    <div className="flex flex-wrap gap-1">
                      {opp.required_skills.map((s) => {
                        const isMatch = compat?.matching_skills.includes(s);
                        return (
                          <span
                            key={s}
                            className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                              isMatch
                                ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                                : "bg-navy-950 text-slate-300 border border-navy-800"
                            }`}
                          >
                            {s}
                          </span>
                        );
                      })}
                    </div>
                  </div>

                  {/* Detail Link */}
                  <Link
                    href={`/opportunities/${opp.id}`}
                    className="w-full text-center py-2 bg-navy-800 hover:bg-navy-700 text-slate-200 text-xs font-semibold rounded-xl transition"
                  >
                    View Complete Profile
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="py-20 text-center text-xs text-slate-400">
          Select at least 2 opportunities to generate a comparative analysis.
        </div>
      )}
    </div>
  );
}
