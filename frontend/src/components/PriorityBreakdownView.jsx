import React from 'react';
import { X, ShieldCheck, Clock, Gauge, Database, AlertCircle } from 'lucide-react';

export default function PriorityBreakdownView({ task, policyMode, onClose }) {
  if (!task) return null;

  const weights = {
    "Safety-First": { wR: 0.50, wI: 0.35, wT: 0.15 },
    "Balanced": { wR: 0.40, wI: 0.35, wT: 0.25 },
    "Throughput-First": { wR: 0.30, wI: 0.35, wT: 0.35 },
  }[policyMode] || { wR: 0.40, wI: 0.35, wT: 0.25 };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-xl rounded-2xl p-6 shadow-2xl relative">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Gauge className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-white">{task.task_id} Priority Breakdown</h2>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                {task.department}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Asset: {task.asset_id} | KM {task.km_from} - {task.km_to} ({task.work_type})
            </p>
          </div>
        </div>

        {/* Dual Primary Metrics (Priority vs Confidence) */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400 block mb-1">Computed Priority (0-100)</span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-blue-400">{task.priority_score}</span>
              <span className="text-xs text-slate-400">/ 100</span>
            </div>
            <span className="text-[11px] text-slate-400 mt-1 block">Mode: {policyMode}</span>
          </div>

          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400 block mb-1">Confidence Rating</span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-emerald-400">
                {(task.confidence_score * 100).toFixed(0)}%
              </span>
              <span className="text-xs text-slate-400">fidelity</span>
            </div>
            <span className="text-[11px] text-amber-400/90 mt-1 block font-medium">
              * Kept separate (Never multiplied)
            </span>
          </div>
        </div>

        {/* 3 Core Indicator Factors: R, I, T */}
        <div className="space-y-3 mb-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Indicator Components & Weights
          </h4>

          {/* R - Risk */}
          <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <ShieldCheck className="w-4 h-4 text-red-400" />
              <div>
                <div className="text-xs font-semibold text-white">Risk Indicator (R)</div>
                <div className="text-[11px] text-slate-400">
                  Severity: {task.severity.toUpperCase()} {task.isolation_required ? "| Isolation required" : ""}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono font-bold text-sm text-white">{task.r_risk}</div>
              <div className="text-[10px] text-slate-400">weight: {weights.wR}</div>
            </div>
          </div>

          {/* I - Operational Impact */}
          <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Gauge className="w-4 h-4 text-amber-400" />
              <div>
                <div className="text-xs font-semibold text-white">Operational Impact (I)</div>
                <div className="text-[11px] text-slate-400">
                  Duration: {task.est_duration_min} min on mainline corridor C-01
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono font-bold text-sm text-white">{task.i_impact}</div>
              <div className="text-[10px] text-slate-400">weight: {weights.wI}</div>
            </div>
          </div>

          {/* T - Time Pressure */}
          <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Clock className="w-4 h-4 text-blue-400" />
              <div>
                <div className="text-xs font-semibold text-white">Time Urgency (T)</div>
                <div className="text-[11px] text-slate-400">
                  Overdue: {task.overdue_days} days | Required within 48h
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono font-bold text-sm text-white">{task.t_time}</div>
              <div className="text-[10px] text-slate-400">weight: {weights.wT}</div>
            </div>
          </div>
        </div>

        {/* Source Telemetry & Audit Meta */}
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <Database className="w-3.5 h-3.5 text-slate-400" />
            <span>Source: <strong className="text-slate-200">{task.source_meta.source}</strong> ({task.source_meta.mode})</span>
          </div>
          <div>Last Sync: {task.source_meta.last_sync}</div>
        </div>

      </div>
    </div>
  );
}
