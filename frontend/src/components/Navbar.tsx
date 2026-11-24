"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Sparkles, Compass, BookmarkCheck, Bot, User, BarChart3, Sliders, LogOut, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setUser(api.getUser());
  }, [pathname]);

  const handleLogout = () => {
    api.clearToken();
    setUser(null);
    router.push("/auth");
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-navy-800/80 bg-navy-950/80 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 shadow-md shadow-brand-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                Match<span className="text-brand-400">IQ</span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                  AI Engine
                </span>
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              href="/dashboard"
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                pathname === "/dashboard"
                  ? "bg-navy-850 text-white border border-navy-700/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-900/60"
              }`}
            >
              Dashboard
            </Link>
            <Link
              href="/discover"
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                pathname.startsWith("/discover")
                  ? "bg-navy-850 text-white border border-navy-700/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-900/60"
              }`}
            >
              Discover
            </Link>
            <Link
              href="/agent"
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center gap-1.5 ${
                pathname.startsWith("/agent")
                  ? "bg-brand-950 text-brand-300 border border-brand-800/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-900/60"
              }`}
            >
              <Bot className="h-3.5 w-3.5 text-brand-400" />
              Career Copilot
            </Link>
            <Link
              href="/saved"
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                pathname.startsWith("/saved")
                  ? "bg-navy-850 text-white border border-navy-700/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-900/60"
              }`}
            >
              Tracker
            </Link>
            <Link
              href="/compare"
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                pathname.startsWith("/compare")
                  ? "bg-navy-850 text-white border border-navy-700/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-900/60"
              }`}
            >
              Compare
            </Link>
            <Link
              href="/evaluation"
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                pathname.startsWith("/evaluation")
                  ? "bg-navy-850 text-white border border-navy-700/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-900/60"
              }`}
            >
              Benchmarks
            </Link>
          </nav>
        </div>

        {/* Right side user / actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <Link
                href="/profile"
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-navy-800 bg-navy-900/80 hover:bg-navy-850 transition"
              >
                <div className="h-6 w-6 rounded-full bg-brand-600/30 border border-brand-500/40 flex items-center justify-center text-xs font-semibold text-brand-300">
                  {user.full_name?.charAt(0) || "U"}
                </div>
                <span className="hidden sm:inline text-xs font-medium text-slate-200">
                  {user.full_name || "Profile"}
                </span>
              </Link>
              <button
                onClick={handleLogout}
                title="Log out"
                className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-navy-850 transition"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/auth"
                className="text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-navy-850 transition"
              >
                Sign In
              </Link>
              <Link
                href="/auth?mode=register"
                className="flex items-center gap-1 text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white px-3.5 py-1.5 rounded-lg transition shadow-sm shadow-brand-500/20"
              >
                Get Started
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
