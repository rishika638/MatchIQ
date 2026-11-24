"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Sparkles, Lock, Mail, User as UserIcon, ArrowRight, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

function AuthContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "register" ? "register" : "login";

  const [mode, setMode] = useState<"login" | "register">(initialMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (api.getUser()) {
      router.push("/dashboard");
    }
  }, [router]);

  const handlePrefillDemo = () => {
    setEmail("candidate@matchiq.ai");
    setPassword("DemoCandidate123!");
    setMode("login");
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "login") {
        const res = await api.login({ email, password });
        api.setToken(res.access_token);
        api.setUser(res.user);
        router.push("/dashboard");
      } else {
        const res = await api.register({
          email,
          password,
          full_name: fullName || "New Candidate",
          role: "candidate"
        });
        api.setToken(res.access_token);
        api.setUser(res.user);
        router.push("/profile");
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-navy-900/90 border border-navy-800 rounded-2xl p-6 sm:p-8 shadow-2xl shadow-navy-950/80">
        {/* Brand header */}
        <div className="text-center mb-8">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 shadow-md shadow-brand-500/20 mb-3">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            {mode === "login" ? "Sign in to MatchIQ" : "Create candidate account"}
          </h2>
          <p className="mt-1.5 text-xs text-slate-400">
            {mode === "login" ? "Access your intelligence dashboard & career copilot" : "Begin your semantic opportunity journey"}
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="flex rounded-xl bg-navy-950/70 p-1 border border-navy-800/80 mb-6">
          <button
            type="button"
            onClick={() => { setMode("login"); setError(null); }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition ${
              mode === "login" ? "bg-navy-850 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setMode("register"); setError(null); }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition ${
              mode === "register" ? "bg-navy-850 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Register
          </button>
        </div>

        {/* Demo Candidate Quick Fill Banner */}
        <div className="mb-6 p-3 rounded-xl border border-brand-500/30 bg-brand-500/10 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-brand-300">
            <CheckCircle2 className="h-4 w-4 text-brand-400 flex-shrink-0" />
            <span>Pre-seeded Demo Candidate</span>
          </div>
          <button
            type="button"
            onClick={handlePrefillDemo}
            className="text-xs font-bold text-white bg-brand-600 hover:bg-brand-500 px-2.5 py-1 rounded-md transition shadow-sm"
          >
            One-Click Fill
          </button>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="mb-6 p-3 rounded-xl border border-rose-500/30 bg-rose-500/10 flex items-center gap-2.5 text-xs text-rose-300">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alex Mercer"
                  className="w-full bg-navy-950 border border-navy-800 rounded-xl pl-9 pr-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="candidate@matchiq.ai"
                className="w-full bg-navy-950 border border-navy-800 rounded-xl pl-9 pr-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-navy-950 border border-navy-800 rounded-xl pl-9 pr-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition shadow-md shadow-brand-500/25 disabled:opacity-50"
          >
            {loading ? "Authenticating..." : mode === "login" ? "Sign In" : "Create Account"}
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense fallback={<div className="min-h-[85vh] flex items-center justify-center text-xs text-slate-400">Loading authentication...</div>}>
      <AuthContent />
    </Suspense>
  );
}
