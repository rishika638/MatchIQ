"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  BarChart3, Compass, BookmarkCheck, Briefcase, Zap, 
  ArrowUpRight, Clock, Target, AlertTriangle, CheckCircle2, ChevronRight 
} from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, PieChart, Pie } from "recharts";
import { api } from "@/lib/api";
import { DashboardMetrics } from "@/types";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await api.getDashboardMetrics();
        setMetrics(data);
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard metrics");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Aggregating database intelligence metrics...</span>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-12 text-center">
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm max-w-md mx-auto">
          {error || "Could not connect to database analytics."}
        </div>
        <Link href="/auth" className="mt-4 inline-block text-xs text-brand-400 underline">
          Please sign in to view your dashboard.
        </Link>
      </div>
    );
  }

  const workModeData = Object.entries(metrics.work_mode_distribution || {}).map(([key, val]) => ({
    name: key.toUpperCase(),
    value: val
  }));

  const COLORS = ["#6366f1", "#8b5cf6", "#3b82f6", "#10b981"];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Intelligence Dashboard</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Database-grounded candidate metrics, skill-gap analysis, and opportunity pipeline.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/discover"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition shadow-md shadow-brand-500/20"
          >
            <Compass className="h-4 w-4" />
            Discover Roles
          </Link>
          <Link
            href="/agent"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-200 border border-navy-700/80 text-xs font-semibold transition"
          >
            <Zap className="h-4 w-4 text-brand-400" />
            Copilot
          </Link>
        </div>
      </div>

      {/* Top 4 KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Card 1 */}
        <div className="p-5 rounded-2xl bg-navy-900/70 border border-navy-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Active Opportunities</span>
            <div className="h-8 w-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Briefcase className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{metrics.total_active_opportunities}</span>
            <span className="text-[11px] text-emerald-400 font-medium">Ingested & Indexed</span>
          </div>
        </div>

        {/* Card 2 */}
        <div className="p-5 rounded-2xl bg-navy-900/70 border border-navy-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Saved Opportunities</span>
            <div className="h-8 w-8 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
              <BookmarkCheck className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{metrics.saved_opportunities}</span>
            <span className="text-[11px] text-slate-400 font-medium">In Tracker</span>
          </div>
        </div>

        {/* Card 3 */}
        <div className="p-5 rounded-2xl bg-navy-900/70 border border-navy-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Submitted Applications</span>
            <div className="h-8 w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{metrics.applied_opportunities}</span>
            <span className="text-[11px] text-slate-400 font-medium">Active Pipeline</span>
          </div>
        </div>

        {/* Card 4 */}
        <div className="p-5 rounded-2xl bg-navy-900/70 border border-navy-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Average Compatibility</span>
            <div className="h-8 w-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Target className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{metrics.average_compatibility}%</span>
            <span className="text-[11px] text-brand-300 font-medium">Heuristic Match</span>
          </div>
        </div>
      </div>

      {/* Middle Section: Skill Gap Insights & Market Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Skill Gap Analysis Bar Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-navy-900/70 border border-navy-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  Target Role Skill Gap Insights
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Most frequent missing required skills across target tech opportunities in your domain.
                </p>
              </div>
            </div>

            {metrics.top_missing_skills && metrics.top_missing_skills.length > 0 ? (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.top_missing_skills} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                    <XAxis type="number" stroke="#64748b" fontSize={11} />
                    <YAxis dataKey="skill" type="category" stroke="#94a3b8" fontSize={12} width={100} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#0b1120", borderColor: "#1e293b", borderRadius: "8px", fontSize: "12px" }}
                      itemStyle={{ color: "#818cf8" }}
                    />
                    <Bar dataKey="demand_count" radius={[0, 6, 6, 0]}>
                      {metrics.top_missing_skills.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? "#6366f1" : "#4f46e5"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-xs text-slate-500">
                No skill gap data recorded yet.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-navy-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Focus prep on high-frequency competencies to maximize interview qualification rates.</span>
            <Link href="/agent" className="text-brand-400 hover:underline flex items-center gap-1 font-semibold">
              Get prep plan <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
        </div>

        {/* Opportunity Work Mode Breakdown */}
        <div className="p-6 rounded-2xl bg-navy-900/70 border border-navy-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white mb-1">Work Mode Distribution</h3>
            <p className="text-xs text-slate-400 mb-4">Breakdown across 100 ingested active tech roles.</p>
            
            <div className="space-y-3">
              {workModeData.map((item, idx) => (
                <div key={item.name} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                    <span className="text-slate-300 font-medium">{item.name}</span>
                  </div>
                  <span className="font-mono text-slate-200">{item.value} roles</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 p-3 rounded-xl bg-navy-950/80 border border-navy-800/80">
            <span className="text-[11px] text-slate-400">
              💡 Hybrid and Remote roles constitute over 80% of verified technical engineering openings.
            </span>
          </div>
        </div>
      </div>

      {/* Recent Activity & Searches */}
      <div className="p-6 rounded-2xl bg-navy-900/70 border border-navy-800">
        <h3 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
          <Clock className="h-4 w-4 text-indigo-400" />
          Recent Hybrid Searches & Activity
        </h3>
        <p className="text-xs text-slate-400 mb-4">Historical queries and measured latency benchmarks.</p>

        {metrics.recent_searches && metrics.recent_searches.length > 0 ? (
          <div className="divide-y divide-navy-800/80">
            {metrics.recent_searches.map((s, idx) => (
              <div key={idx} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2.5">
                  <span className="px-2 py-0.5 rounded bg-navy-800 text-brand-300 font-mono text-[10px]">
                    {s.retrieval_method}
                  </span>
                  <span className="text-slate-200 font-medium">&quot;{s.query}&quot;</span>
                </div>
                <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                  <span>{s.result_count} results</span>
                  <span>{s.latency_ms} ms</span>
                  <Link
                    href={`/discover?q=${encodeURIComponent(s.query)}`}
                    className="text-brand-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    Re-run <ArrowUpRight className="h-3 w-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-slate-500">
            No recent search history. <Link href="/discover" className="text-brand-400 underline">Try searching for backend roles.</Link>
          </div>
        )}
      </div>
    </div>
  );
}
