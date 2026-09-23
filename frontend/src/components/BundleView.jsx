import React, { useState } from 'react';
import { GitMerge, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';

export default function BundleView({ bundles }) {
  const [activeTab, setActiveTab] = useState("ALL"); // ALL, ACCEPTED, REJECTED

  const accepted = bundles.filter(b => b.is_bundleable);
  const rejected = bundles.filter(b => !b.is_bundleable);

  const displayList = activeTab === "ALL" 
    ? bundles 
    : activeTab === "ACCEPTED" ? accepted : rejected;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-wrap items-center justify-between mb-4 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <GitMerge className="w-5 h-5 text-indigo-400" />
            <h3 className="font-bold text-base text-white">Auto-Shadow Bundling Gate</h3>
          </div>
          <p className="text-xs text-slate-400">
            Deterministic gate chain evaluation: Corridor → KM → Time → Resources → Dependencies → Isolation
          </p>
        </div>

        {/* Tab Filters */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab("ALL")}
            className={`px-3 py-1 rounded-lg font-medium transition-all ${
              activeTab === "ALL" ? "bg-slate-800 text-white font-semibold" : "text-slate-400 hover:text-white"
            }`}
          >
            All Evaluated Pairs ({bundles.length})
          </button>
          <button
            onClick={() => setActiveTab("ACCEPTED")}
            className={`px-3 py-1 rounded-lg font-medium transition-all ${
              activeTab === "ACCEPTED" ? "bg-emerald-950 text-emerald-300 font-semibold" : "text-slate-400 hover:text-emerald-300"
            }`}
          >
            Accepted Bundles ({accepted.length})
          </button>
          <button
            onClick={() => setActiveTab("REJECTED")}
            className={`px-3 py-1 rounded-lg font-medium transition-all ${
              activeTab === "REJECTED" ? "bg-red-950 text-red-300 font-semibold" : "text-slate-400 hover:text-red-300"
            }`}
          >
            Rejected Collisions ({rejected.length})
          </button>
        </div>
      </div>

      {/* Candidate Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {displayList.slice(0, 10).map((b, idx) => (
          <div
            key={`${b.task_a_id}-${b.task_b_id}-${idx}`}
            className={`p-4 rounded-xl border transition-all ${
              b.is_bundleable
                ? "bg-emerald-950/20 border-emerald-500/30 hover:border-emerald-500/50"
                : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
            }`}
          >
            {/* Header: Pair + Status */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-white text-sm bg-slate-800 px-2 py-0.5 rounded">
                  {b.task_a_id}
                </span>
                <span className="text-slate-400 font-mono text-xs">+</span>
                <span className="font-bold text-white text-sm bg-slate-800 px-2 py-0.5 rounded">
                  {b.task_b_id}
                </span>
              </div>

              {b.is_bundleable ? (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  <CheckCircle className="w-3.5 h-3.5 mr-1" /> WHY BUNDLE
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-300 border border-red-500/40">
                  <XCircle className="w-3.5 h-3.5 mr-1" /> WHY NOT
                </span>
              )}
            </div>

            {/* Explanation Message */}
            <p className="text-xs text-slate-300 mb-3 leading-relaxed">
              {b.reason_message}
            </p>

            {/* Footer: Time Saved or Reason Code */}
            <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
              {b.is_bundleable ? (
                <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Est. Block Time Saved: ~{b.estimated_time_saved_min} mins</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1.5 text-red-400 font-medium font-mono text-[11px]">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Reason: {b.reason_code || "REJECTED"}</span>
                </div>
              )}
              <span className="text-[11px] text-slate-500">Corridor C-01</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
