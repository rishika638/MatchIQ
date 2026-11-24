"use client";

import React, { useEffect, useState } from "react";
import { 
  BarChart3, Cpu, Sparkles, RefreshCw, CheckCircle2, 
  Layers, Clock, Award, TrendingUp, Zap, HelpCircle 
} from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import { api } from "@/lib/api";
import { EvaluationRun } from "@/types";

export default function EvaluationPage() {
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [queries, setQueries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningSuite, setRunningSuite] = useState(false);
  const [suiteMessage, setSuiteMessage] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [runsData, queriesData] = await Promise.all([
        api.getEvaluationRuns(),
        api.getBenchmarkQueries()
      ]);
      setRuns(runsData || []);
      setQueries(queriesData || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunFullSuite = async () => {
    setRunningSuite(true);
    setSuiteMessage(null);
    try {
      const res = await api.runFullEvaluation();
      setSuiteMessage(`Successfully benchmarked ${res.runs_completed} retrieval methods across all ${queries.length} labelled queries!`);
      loadData();
    } catch (err: any) {
      setSuiteMessage(`Evaluation error: ${err.message}`);
    } finally {
      setRunningSuite(false);
    }
  };

  // Prepare chart comparison data
  const latestByMethod: Record<string, EvaluationRun> = {};
  for (const r of runs) {
    if (!latestByMethod[r.retrieval_method]) {
      latestByMethod[r.retrieval_method] = r;
    }
  }

  const comparisonChartData = [
    {
      method: "Keyword (FTS)",
      key: "keyword",
      MRR: latestByMethod["keyword"]?.mrr || 0,
      NDCG_5: latestByMethod["keyword"]?.ndcg_at_k?.["k=5"] || 0,
      P_3: latestByMethod["keyword"]?.precision_at_k?.["k=3"] || 0,
      Latency: latestByMethod["keyword"]?.average_latency_ms || 0
    },
    {
      method: "Semantic (Dense)",
      key: "semantic",
      MRR: latestByMethod["semantic"]?.mrr || 0,
      NDCG_5: latestByMethod["semantic"]?.ndcg_at_k?.["k=5"] || 0,
      P_3: latestByMethod["semantic"]?.precision_at_k?.["k=3"] || 0,
      Latency: latestByMethod["semantic"]?.average_latency_ms || 0
    },
    {
      method: "Hybrid (RRF)",
      key: "hybrid",
      MRR: latestByMethod["hybrid"]?.mrr || 0,
      NDCG_5: latestByMethod["hybrid"]?.ndcg_at_k?.["k=5"] || 0,
      P_3: latestByMethod["hybrid"]?.precision_at_k?.["k=3"] || 0,
      Latency: latestByMethod["hybrid"]?.average_latency_ms || 0
    },
    {
      method: "Hybrid + Reranked",
      key: "hybrid_reranked",
      MRR: latestByMethod["hybrid_reranked"]?.mrr || 0,
      NDCG_5: latestByMethod["hybrid_reranked"]?.ndcg_at_k?.["k=5"] || 0,
      P_3: latestByMethod["hybrid_reranked"]?.precision_at_k?.["k=3"] || 0,
      Latency: latestByMethod["hybrid_reranked"]?.average_latency_ms || 0
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs font-semibold mb-2">
            <Award className="h-3.5 w-3.5" />
            <span>Reproducible Benchmark Suite • Ground Truth Judgments</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Evaluation & Retrieval Benchmarking
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Empirical comparison of Keyword, Dense Semantic, RRF Hybrid, and Cross-Encoder Reranking retrieval paradigms.
          </p>
        </div>

        <button
          onClick={handleRunFullSuite}
          disabled={runningSuite}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition shadow-md shadow-brand-500/25 disabled:opacity-50"
        >
          {runningSuite ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
          {runningSuite ? "Evaluating Queries..." : "Run Benchmark Suite"}
        </button>
      </div>

      {suiteMessage && (
        <div className="mb-6 p-4 rounded-xl bg-navy-900 border border-brand-500/30 text-xs text-brand-300 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
          <span>{suiteMessage}</span>
        </div>
      )}

      {/* Main Comparison Chart: NDCG@5 & MRR */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Quality Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-navy-900/70 border border-navy-800 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-brand-400" />
              Retrieval Quality Comparison (NDCG@5, MRR & Precision@3)
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Higher is better. Measures top-rank ranking precision against graded ground-truth relevance.
            </p>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonChartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="method" stroke="#64748b" fontSize={11} />
                  <YAxis domain={[0, 1.0]} stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: "#0b1120", borderColor: "#1e293b", fontSize: "11px" }} />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                  <Bar dataKey="NDCG_5" name="NDCG@5" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="MRR" name="MRR" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="P_3" name="Precision@3" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-navy-800 text-[11px] text-slate-400">
            ✓ <strong>Hybrid (RRF)</strong> improves Recall and NDCG over standalone dense vector and keyword BM25 retrieval.
          </div>
        </div>

        {/* Latency Comparison */}
        <div className="p-6 rounded-2xl bg-navy-900/70 border border-navy-800 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
              <Clock className="h-4 w-4 text-indigo-400" />
              Retrieval Latency (ms)
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Average query processing round-trip latency.
            </p>

            <div className="space-y-4">
              {comparisonChartData.map((item) => (
                <div key={item.key} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">{item.method}</span>
                    <span className="font-mono text-slate-200">{item.Latency} ms</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-navy-950 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-indigo-500 rounded-full"
                      style={{ width: `${Math.min(100, Math.max(5, item.Latency * 2))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 p-3 rounded-xl bg-navy-950 border border-navy-800 text-[11px] text-slate-400">
            Cross-encoder reranking introduces slight latency in exchange for elevated attention accuracy.
          </div>
        </div>
      </div>

      {/* Benchmark Runs Table */}
      <div className="p-6 rounded-2xl bg-navy-900/70 border border-navy-800 mb-8">
        <h2 className="text-sm font-bold text-white mb-1">Historical Quantitative Benchmark Runs</h2>
        <p className="text-xs text-slate-400 mb-4">
          All calculated metrics are persisted in PostgreSQL <code>evaluation_runs</code>.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-950 text-slate-400 border-b border-navy-800 font-mono">
              <tr>
                <th className="py-2.5 px-3">Run ID</th>
                <th className="py-2.5 px-3">Method</th>
                <th className="py-2.5 px-3">MRR</th>
                <th className="py-2.5 px-3">NDCG@5</th>
                <th className="py-2.5 px-3">P@3</th>
                <th className="py-2.5 px-3">Recall@5</th>
                <th className="py-2.5 px-3">Latency</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-800/80 font-mono">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-navy-850/50 transition">
                  <td className="py-2.5 px-3 text-brand-300">{r.id.slice(0, 8)}...</td>
                  <td className="py-2.5 px-3 font-sans font-medium text-slate-200 capitalize">
                    {r.retrieval_method.replace("_", " ")}
                  </td>
                  <td className="py-2.5 px-3 text-slate-100">{r.mrr}</td>
                  <td className="py-2.5 px-3 text-slate-100">{r.ndcg_at_k?.["k=5"] || "0.0"}</td>
                  <td className="py-2.5 px-3 text-slate-100">{r.precision_at_k?.["k=3"] || "0.0"}</td>
                  <td className="py-2.5 px-3 text-slate-100">{r.recall_at_k?.["k=5"] || "0.0"}</td>
                  <td className="py-2.5 px-3 text-emerald-400">{r.average_latency_ms} ms</td>
                  <td className="py-2.5 px-3 text-slate-500 font-sans">{new Date(r.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Labelled Evaluation Benchmark Queries */}
      <div className="p-6 rounded-2xl bg-navy-900/70 border border-navy-800">
        <h2 className="text-sm font-bold text-white mb-1">Ground Truth Benchmark Queries</h2>
        <p className="text-xs text-slate-400 mb-4">
          Labelled evaluation dataset loaded from <code>data/evaluation/evaluation_benchmark.json</code>.
        </p>

        <div className="divide-y divide-navy-800/80">
          {queries.map((q) => (
            <div key={q.query_id} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <div>
                <span className="font-mono text-brand-400 mr-2">[{q.query_id}]</span>
                <span className="text-slate-200 font-medium">&quot;{q.query_text}&quot;</span>
                <p className="text-[11px] text-slate-400 mt-0.5">{q.intent}</p>
              </div>
              <span className="text-[11px] text-slate-500 whitespace-nowrap">
                {q.judged_opportunities_count} judged opportunities
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
