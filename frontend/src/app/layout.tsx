import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "MatchIQ — Opportunity Intelligence Engine",
  description: "Next-generation AI-powered career opportunity discovery, semantic hybrid retrieval, explainable matching, and career intelligence agent.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-navy-950 text-slate-100 antialiased flex flex-col selection:bg-brand-500/30 selection:text-brand-200">
        <Navbar />
        <main className="flex-1 w-full flex flex-col">
          {children}
        </main>
        <footer className="border-t border-navy-800/60 bg-navy-950/60 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p>MatchIQ Opportunity Intelligence Engine • Built with Next.js, FastAPI & PostgreSQL pgvector</p>
            <div className="flex items-center gap-4 text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Deterministic AI Vector Search Active
              </span>
              <span>v1.0.0</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
