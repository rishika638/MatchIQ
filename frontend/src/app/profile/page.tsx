"use client";

import React, { useState, useEffect } from "react";
import { 
  User, FileText, Upload, Sparkles, Plus, Trash2, Check, 
  AlertCircle, Briefcase, MapPin, DollarSign, RefreshCw 
} from "lucide-react";
import { api } from "@/lib/api";
import { CandidateProfile } from "@/types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  // Form states
  const [headline, setHeadline] = useState("");
  const [bio, setBio] = useState("");
  const [experienceYears, setExperienceYears] = useState<number>(0);
  const [skills, setSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState("");
  const [locations, setLocations] = useState<string[]>([]);
  const [newLocation, setNewLocation] = useState("");
  const [workModes, setWorkModes] = useState<string[]>([]);
  const [opportunityTypes, setOpportunityTypes] = useState<string[]>([]);
  const [minSalary, setMinSalary] = useState<number>(0);
  const [roles, setRoles] = useState<string[]>([]);
  const [newRole, setNewRole] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        setLoading(true);
        const data = await api.getProfile();
        setProfile(data);
        setHeadline(data.headline || "");
        setBio(data.bio || "");
        setExperienceYears(data.experience_years || 0);
        setSkills(data.skills || []);
        setLocations(data.preferred_locations || []);
        setWorkModes(data.preferred_work_modes || ["remote", "hybrid"]);
        setOpportunityTypes(data.preferred_opportunity_types || ["full-time"]);
        setMinSalary(data.preferred_min_salary || 0);
        setRoles(data.preferred_roles || []);
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await api.updateProfile({
        headline,
        bio,
        experience_years: Number(experienceYears),
        skills,
        preferred_locations: locations,
        preferred_work_modes: workModes,
        preferred_opportunity_types: opportunityTypes,
        preferred_min_salary: Number(minSalary),
        preferred_roles: roles,
      });
      setProfile(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.uploadResume(formData);
      const preview = res.extracted_preview;
      if (preview) {
        if (preview.headline) setHeadline(preview.headline);
        if (preview.experience_years) setExperienceYears(preview.experience_years);
        if (preview.skills && preview.skills.length > 0) {
          // Merge unique skills
          const merged = Array.from(new Set([...skills, ...preview.skills]));
          setSkills(merged);
        }
        if (preview.preferred_roles && preview.preferred_roles.length > 0) {
          setRoles(Array.from(new Set([...roles, ...preview.preferred_roles])));
        }
      }
      setUploadMessage(`Successfully parsed "${file.name}". Extracted ${preview?.skills?.length || 0} skills and background. Review and save below.`);
    } catch (err: any) {
      setUploadMessage(`Upload error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill("");
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter((s) => s !== skillToRemove));
  };

  const toggleWorkMode = (mode: string) => {
    if (workModes.includes(mode)) {
      setWorkModes(workModes.filter((m) => m !== mode));
    } else {
      setWorkModes([...workModes, mode]);
    }
  };

  const toggleType = (t: string) => {
    if (opportunityTypes.includes(t)) {
      setOpportunityTypes(opportunityTypes.filter((x) => x !== t));
    } else {
      setOpportunityTypes([...opportunityTypes, t]);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Loading candidate profile...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Candidate Profile & Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage your professional skills, career constraints, and extracted resume intelligence.
          </p>
        </div>

        {saveSuccess && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold animate-fade-in">
            <Check className="h-4 w-4" />
            Profile changes saved successfully!
          </div>
        )}
      </div>

      {/* Resume Upload Box */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-navy-900 via-navy-900/90 to-brand-950/30 border border-brand-500/30 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-brand-500/10 text-brand-300 text-xs font-semibold border border-brand-500/20 mb-2">
              <Sparkles className="h-3.5 w-3.5 text-brand-400" />
              Automated Resume Extraction
            </span>
            <h2 className="text-base font-bold text-white">Upload Resume (PDF or TXT)</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Extract technical skills, experience tenure, and education automatically into your profile.
            </p>
          </div>

          <label className="cursor-pointer px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition flex items-center justify-center gap-2 shadow-md shadow-brand-500/20 whitespace-nowrap">
            {uploading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            {uploading ? "Parsing File..." : "Upload Resume File"}
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>

        {uploadMessage && (
          <div className="mt-4 p-3 rounded-xl bg-navy-950/80 border border-navy-800 text-xs text-slate-200 flex items-center gap-2">
            <Check className="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>{uploadMessage}</span>
          </div>
        )}
      </div>

      {/* Main Profile Edit Form */}
      <form onSubmit={handleSaveProfile} className="space-y-6">
        {/* Basic Details */}
        <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800 space-y-4">
          <h2 className="text-sm font-bold text-white mb-2">Professional Headline & Summary</h2>
          
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Headline</label>
            <input
              type="text"
              value={headline}
              onChange={(e) => setHeadline(e.target.value)}
              placeholder="e.g. Senior Distributed Systems & AI Backend Engineer"
              className="w-full bg-navy-950 border border-navy-800 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Total Years of Experience</label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={experienceYears}
                onChange={(e) => setExperienceYears(parseFloat(e.target.value) || 0)}
                className="w-full bg-navy-950 border border-navy-800 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Target Annual Salary ($ USD)</label>
              <input
                type="number"
                step="5000"
                min="0"
                value={minSalary}
                onChange={(e) => setMinSalary(parseInt(e.target.value) || 0)}
                className="w-full bg-navy-950 border border-navy-800 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Professional Bio / Elevator Pitch</label>
            <textarea
              rows={3}
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Summary of engineering focus, technical milestones, and architectural experience..."
              className="w-full bg-navy-950 border border-navy-800 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
            />
          </div>
        </div>

        {/* Technical Skills Manager */}
        <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800">
          <h2 className="text-sm font-bold text-white mb-1">Technical Skills & Competencies</h2>
          <p className="text-xs text-slate-400 mb-4">
            These skills power the semantic matching and gap analysis engine against opportunity requirements.
          </p>

          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addSkill(); } }}
              placeholder="Add skill (e.g. Distributed Systems, Ray, Kafka)..."
              className="flex-1 bg-navy-950 border border-navy-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition"
            />
            <button
              type="button"
              onClick={addSkill}
              className="px-4 py-2 bg-navy-800 hover:bg-navy-700 text-slate-200 text-xs font-semibold rounded-xl transition flex items-center gap-1.5"
            >
              <Plus className="h-4 w-4" /> Add
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {skills.map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 rounded-lg bg-navy-950 border border-navy-700/80 text-xs font-medium text-slate-200 flex items-center gap-1.5 group"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="text-slate-500 hover:text-rose-400 transition"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Career Preferences */}
        <div className="p-6 rounded-2xl bg-navy-900/60 border border-navy-800 space-y-4">
          <h2 className="text-sm font-bold text-white mb-2">Work Preferences & Constraints</h2>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Target Work Modes</label>
            <div className="flex flex-wrap gap-2">
              {["remote", "hybrid", "onsite"].map((mode) => {
                const active = workModes.includes(mode);
                return (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => toggleWorkMode(mode)}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold capitalize transition border ${
                      active
                        ? "bg-brand-600/20 border-brand-500/50 text-brand-300"
                        : "bg-navy-950 border-navy-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {mode}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Target Opportunity Types</label>
            <div className="flex flex-wrap gap-2">
              {["full-time", "contract", "internship", "part-time"].map((t) => {
                const active = opportunityTypes.includes(t);
                return (
                  <button
                    key={t}
                    type="button"
                    onClick={() => toggleType(t)}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold capitalize transition border ${
                      active
                        ? "bg-brand-600/20 border-brand-500/50 text-brand-300"
                        : "bg-navy-950 border-navy-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {t}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2"
        >
          {saving ? "Saving Changes..." : "Save Candidate Profile"}
        </button>
      </form>
    </div>
  );
}
