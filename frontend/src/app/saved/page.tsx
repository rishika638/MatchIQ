"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Bookmark, BookmarkCheck, Building2, MapPin, DollarSign, 
  Trash2, ExternalLink, ArrowRight, CheckCircle2, Clock, Briefcase 
} from "lucide-react";
import { api } from "@/lib/api";
import { SavedOpportunityItem } from "@/types";

const STATUS_TABS = [
  { id: "", label: "All Items" },
  { id: "saved", label: "Saved" },
  { id: "applied", label: "Applied" },
  { id: "interviewing", label: "Interviewing" },
  { id: "offered", label: "Offered" },
  { id: "archived", label: "Archived" }
];

export default function SavedTrackerPage() {
  const [items, setItems] = useState<SavedOpportunityItem[]>([]);
  const [activeTab, setActiveTab] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const loadSaved = async (statusFilter = activeTab) => {
    try {
      setLoading(true);
      const data = await api.getSavedOpportunities(statusFilter || undefined);
      setItems(data);
    } catch (err) {
      console.error("Failed to load saved items:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSaved(activeTab);
  }, [activeTab]);

  const handleStatusChange = async (oppId: string, newStatus: string) => {
    try {
      await api.updateSavedStatus(oppId, { status: newStatus });
      setItems((prev) =>
        prev.map((item) => (item.opportunity_id === oppId ? { ...item, status: newStatus } : item))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemove = async (oppId: string) => {
    try {
      await api.removeSaved(oppId);
      setItems((prev) => prev.filter((item) => item.opportunity_id !== oppId));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Saved Opportunities Tracker</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Track and manage your application lifecycle stages from discovery through offer.
          </p>
        </div>

        <Link
          href="/discover"
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition shadow-md shadow-brand-500/20"
        >
          Discover More Opportunities
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex flex-wrap gap-1.5 p-1 rounded-xl bg-navy-900/60 border border-navy-800 mb-6">
        {STATUS_TABS.map((tab) => {
          const count = tab.id
            ? items.filter((i) => i.status === tab.id).length
            : items.length;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === tab.id
                  ? "bg-navy-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tracker Items List */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Loading tracked opportunities...</span>
        </div>
      ) : items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map((item) => {
            const opp = item.opportunity;
            if (!opp) return null;
            const compat = item.compatibility;

            return (
              <div
                key={item.id}
                className="p-5 rounded-2xl bg-navy-900/70 border border-navy-800 flex flex-col justify-between gap-4"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <span className="text-[10px] font-mono text-brand-300 px-2 py-0.5 rounded bg-navy-950 border border-navy-800">
                        {opp.id}
                      </span>
                      <h2 className="text-base font-bold text-white hover:text-brand-300 transition mt-1.5">
                        <Link href={`/opportunities/${opp.id}`}>{opp.title}</Link>
                      </h2>
                      <p className="text-xs font-semibold text-slate-300">
                        {opp.company} • <span className="text-slate-400 font-normal">{opp.location}</span>
                      </p>
                    </div>

                    {compat && (
                      <div className="h-9 w-9 rounded-full bg-brand-600/20 border border-brand-500/40 flex items-center justify-center font-bold text-xs text-brand-300 font-mono flex-shrink-0">
                        {Math.round(compat.overall_compatibility)}%
                      </div>
                    )}
                  </div>

                  <p className="text-xs text-slate-400 line-clamp-2 mt-2 leading-relaxed">
                    {opp.description}
                  </p>
                </div>

                {/* Status selector & Actions */}
                <div className="pt-3 border-t border-navy-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500 text-[11px]">Stage:</span>
                    <select
                      value={item.status}
                      onChange={(e) => handleStatusChange(item.opportunity_id, e.target.value)}
                      className="bg-navy-950 border border-navy-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none font-medium capitalize"
                    >
                      <option value="saved">Saved</option>
                      <option value="applied">Applied</option>
                      <option value="interviewing">Interviewing</option>
                      <option value="offered">Offered</option>
                      <option value="archived">Archived</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link
                      href={`/opportunities/${opp.id}`}
                      className="p-1.5 text-slate-400 hover:text-white transition rounded-lg hover:bg-navy-850"
                      title="View Details"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Link>
                    <button
                      onClick={() => handleRemove(item.opportunity_id)}
                      className="p-1.5 text-slate-500 hover:text-rose-400 transition rounded-lg hover:bg-navy-850"
                      title="Remove from tracker"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-20 text-center bg-navy-900/40 border border-navy-800 rounded-2xl p-8">
          <p className="text-sm text-slate-400">No tracked opportunities found in this category.</p>
          <Link
            href="/discover"
            className="mt-4 inline-block px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold"
          >
            Discover Opportunities
          </Link>
        </div>
      )}
    </div>
  );
}
