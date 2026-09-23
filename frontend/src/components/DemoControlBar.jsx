import React from 'react';
import { AlertTriangle, WifiOff, Cpu, RotateCcw } from 'lucide-react';

export default function DemoControlBar({
  onEmergency,
  onToggleTdms,
  tdmsOnline,
  onResolveSchedule,
  onReset,
  loading,
}) {
  return (
    <div className="bg-slate-900 border-b border-slate-800 px-6 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold uppercase tracking-wider text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded border border-amber-400/20">
            Live Hackathon Demo Controls
          </span>
          <span className="text-xs text-slate-400 hidden sm:inline">
            Demonstrate real-time reactivity, health gates, and CP-SAT re-solve:
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Emergency Injection Button */}
          <button
            onClick={onEmergency}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/40 text-xs font-semibold transition-colors disabled:opacity-50"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
            <span>Simulate Rail Fracture (Emergency)</span>
          </button>

          {/* Toggle TDMS Telemetry */}
          <button
            onClick={onToggleTdms}
            disabled={loading}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors disabled:opacity-50 ${
              tdmsOnline
                ? "bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border-amber-500/40"
                : "bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border-emerald-500/40"
            }`}
          >
            <WifiOff className="w-3.5 h-3.5" />
            <span>{tdmsOnline ? "Simulate TDMS Telemetry Outage (STALE)" : "Restore TDMS Telemetry"}</span>
          </button>

          {/* Re-solve Schedule */}
          <button
            onClick={onResolveSchedule}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors shadow-sm disabled:opacity-50"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Re-solve CP-SAT Schedule</span>
          </button>

          {/* Reset State */}
          <button
            onClick={onReset}
            disabled={loading}
            title="Reset to default scenario"
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
