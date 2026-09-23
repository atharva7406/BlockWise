import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, ArrowUpDown } from 'lucide-react';

export default function TaskListView({ tasks, onSelectTask }) {
  const [filter, setFilter] = useState("ALL");

  const filteredTasks = filter === "ALL" 
    ? tasks 
    : tasks.filter(t => t.health_state === filter);

  const getHealthBadge = (state) => {
    switch (state) {
      case "VALID":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3 mr-1" /> VALID
          </span>
        );
      case "STALE":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3 mr-1" /> STALE
          </span>
        );
      case "CONFLICTED":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/30">
            <HelpCircle className="w-3 h-3 mr-1" /> CONFLICTED
          </span>
        );
      case "QUARANTINED":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/30">
            <AlertOctagon className="w-3 h-3 mr-1" /> QUARANTINED
          </span>
        );
      default:
        return null;
    }
  };

  const counts = {
    ALL: tasks.length,
    VALID: tasks.filter(t => t.health_state === "VALID").length,
    STALE: tasks.filter(t => t.health_state === "STALE").length,
    CONFLICTED: tasks.filter(t => t.health_state === "CONFLICTED").length,
    QUARANTINED: tasks.filter(t => t.health_state === "QUARANTINED").length,
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
      {/* Header & Health State Filters */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="font-bold text-base text-white">Maintenance Task Registry</h3>
          <p className="text-xs text-slate-400">Validated through Data Health Gate state machine</p>
        </div>

        <div className="flex flex-wrap gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          {["ALL", "VALID", "STALE", "CONFLICTED", "QUARANTINED"].map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                filter === st
                  ? "bg-slate-800 text-white font-semibold shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {st} ({counts[st]})
            </button>
          ))}
        </div>
      </div>

      {/* Task Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3">Task ID</th>
              <th className="py-2.5 px-3">Dept</th>
              <th className="py-2.5 px-3">Asset & Chainage</th>
              <th className="py-2.5 px-3">Work Type</th>
              <th className="py-2.5 px-3">Health Status</th>
              <th className="py-2.5 px-3">Priority</th>
              <th className="py-2.5 px-3">Confidence</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredTasks.map((t) => (
              <tr
                key={t.task_id}
                className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                onClick={() => onSelectTask(t)}
              >
                <td className="py-3 px-3 font-bold text-white">
                  {t.task_id}
                </td>
                <td className="py-3 px-3">
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                    t.department === "ENGG" ? "bg-amber-950 text-amber-300 border border-amber-800" :
                    t.department === "S&T" ? "bg-emerald-950 text-emerald-300 border border-emerald-800" :
                    "bg-purple-950 text-purple-300 border border-purple-800"
                  }`}>
                    {t.department}
                  </span>
                </td>
                <td className="py-3 px-3">
                  <div className="font-medium text-slate-200">{t.asset_id}</div>
                  <div className="text-[11px] text-slate-400">KM {t.km_from} - {t.km_to}</div>
                </td>
                <td className="py-3 px-3 capitalize">
                  {t.work_type.replace(/_/g, " ")}
                </td>
                <td className="py-3 px-3">
                  {getHealthBadge(t.health_state)}
                </td>
                <td className="py-3 px-3">
                  <div className="flex items-center space-x-1.5">
                    <span className="font-bold text-white text-sm">{t.priority_score}</span>
                    <span className="text-[10px] text-slate-400">/ 100</span>
                  </div>
                </td>
                <td className="py-3 px-3">
                  <div className="flex items-center space-x-1">
                    <div className="w-12 bg-slate-800 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          t.confidence_score >= 0.8 ? "bg-emerald-500" :
                          t.confidence_score >= 0.5 ? "bg-amber-500" : "bg-red-500"
                        }`}
                        style={{ width: `${t.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-[11px] text-slate-400">{(t.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="py-3 px-3 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectTask(t);
                    }}
                    className="text-blue-400 hover:text-blue-300 text-xs font-semibold hover:underline"
                  >
                    Breakdown →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
