"use client";

import React, { useState, useEffect } from "react";
import { 
  Sliders, Database, Upload, RefreshCw, CheckCircle2, 
  ShieldCheck, Cpu, Key, FileText, AlertCircle 
} from "lucide-react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [reindexing, setReindexing] = useState(false);
  const [reindexMsg, setReindexMsg] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setUser(api.getUser());
  }, []);

  const handleReindex = async () => {
    setReindexing(true);
    setReindexMsg(null);
    try {
      const res = await api.reindexEmbeddings();
      setReindexMsg(res.message);
    } catch (err: any) {
      setReindexMsg(`Reindex error: ${err.message}`);
    } finally {
      setReindexing(false);
    }
  };

  const handleDatasetUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMsg(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("matchiq_token");
      const res = await fetch("http://localhost:8000/api/v1/ingestion/upload", {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ingestion failed");

      setUploadMsg(`Job ${data.job_id} complete: ${data.successful_records} opportunities ingested successfully (${data.failed_records} failed).`);
    } catch (err: any) {
      setUploadMsg(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">System Settings & Data Pipeline</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Configure multi-tenant parameters, ingest new opportunity datasets, and manage AI embeddings.
        </p>
      </div>

      <div className="space-y-6">
        {/* Workspace Identity */}
        <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
          <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-brand-400" />
            Tenant & Workspace Isolation
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            MatchIQ enforces strict tenant isolation boundaries across users and enterprise workspaces.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-500 block text-[10px] font-sans">Active User</span>
              <span className="text-slate-200">{user?.email || "candidate@matchiq.ai"}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-500 block text-[10px] font-sans">Tenant Role</span>
              <span className="text-brand-300 capitalize">{user?.role || "candidate"}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-500 block text-[10px] font-sans">Isolation Mode</span>
              <span className="text-emerald-400">Strict Multi-Tenant</span>
            </div>
          </div>
        </div>

        {/* AI Configuration */}
        <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
          <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-indigo-400" />
            Configured AI Models & Embeddings
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Engineered models powering dense semantic search, cross-encoder reranking, and career intelligence.
          </p>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-white block">Bi-Encoder Embeddings</span>
                <span className="text-slate-400 text-[11px]">all-MiniLM-L6-v2 (384-dimensional dense vectors)</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-mono text-[10px]">Active</span>
            </div>

            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-white block">Cross-Encoder Reranker</span>
                <span className="text-slate-400 text-[11px]">ms-marco-MiniLM-L-6-v2 (Deep cross-attention scoring)</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 font-mono text-[10px]">Configurable</span>
            </div>

            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <div>
                <span className="font-semibold text-white block">AI Agent LLM</span>
                <span className="text-slate-400 text-[11px]">Google Gemini 2.0 Flash + Deterministic Tool Calling Fallback</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-mono text-[10px]">Dual-Engine</span>
            </div>
          </div>
        </div>

        {/* Ingestion Pipeline */}
        <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
          <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
            <Database className="h-4 w-4 text-emerald-400" />
            Opportunity Data Ingestion
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Upload new CSV or JSON opportunity records to expand the intelligence database.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <label className="cursor-pointer px-4 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-700 text-slate-200 text-xs font-semibold transition border border-navy-700 flex items-center gap-2">
              <Upload className="h-4 w-4" />
              {uploading ? "Ingesting Records..." : "Upload Opportunity CSV / JSON"}
              <input
                type="file"
                accept=".json,.csv"
                onChange={handleDatasetUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>

            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="px-4 py-2.5 rounded-xl bg-navy-950 border border-navy-800 hover:border-brand-500/50 text-slate-300 hover:text-white text-xs font-semibold transition flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${reindexing ? "animate-spin" : ""}`} />
              {reindexing ? "Re-indexing Vectors..." : "Re-index All Embeddings"}
            </button>
          </div>

          {uploadMsg && (
            <div className="mt-4 p-3 rounded-xl bg-navy-950 border border-navy-800 text-xs text-emerald-300 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
              <span>{uploadMsg}</span>
            </div>
          )}

          {reindexMsg && (
            <div className="mt-4 p-3 rounded-xl bg-navy-950 border border-navy-800 text-xs text-brand-300 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
              <span>{reindexMsg}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
