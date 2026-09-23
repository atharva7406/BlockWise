import React from 'react';
import { ShieldAlert, Train, Activity, Settings2 } from 'lucide-react';

export default function Navbar({ policyMode, onPolicyChange, taskCount }) {
  return (
    <header className="bg-slate-900/90 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-md px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-inner">
            <Train className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">RailPlan PS-27</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-950 text-blue-300 border border-blue-800">
                SIH26027 Prototype
              </span>
            </div>
            <p className="text-xs text-slate-400">Automatic Maintenance Block Planning & Auto-Shadow Bundling</p>
          </div>
        </div>

        {/* Corridor & Active Stats */}
        <div className="hidden md:flex items-center space-x-6 text-xs text-slate-300">
          <div className="flex items-center space-x-1.5 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
            <span className="text-slate-400">Corridor:</span>
            <span className="font-semibold text-emerald-400">C-01 (KM 100 - 160)</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
            <Activity className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
            <span className="text-slate-400">Active Tasks:</span>
            <span className="font-semibold text-white">{taskCount}</span>
          </div>
        </div>

        {/* Policy Mode Selector */}
        <div className="flex items-center space-x-2 bg-slate-800/80 p-1 rounded-xl border border-slate-700">
          <div className="flex items-center px-2 text-xs text-slate-400 font-medium">
            <Settings2 className="w-3.5 h-3.5 mr-1" /> Policy:
          </div>
          {["Safety-First", "Balanced", "Throughput-First"].map((mode) => (
            <button
              key={mode}
              onClick={() => onPolicyChange(mode)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                policyMode === mode
                  ? "bg-blue-600 text-white shadow-sm font-semibold"
                  : "text-slate-300 hover:text-white hover:bg-slate-700/50"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>

      </div>
    </header>
  );
}
