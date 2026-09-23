import React from 'react';
import { Calendar, Cpu, CheckCircle2, UserCheck, AlertCircle, Sparkles } from 'lucide-react';

export default function ScheduleGanttView({ schedule, stats, onOfficerAction }) {
  // Group schedule blocks by window_id
  const windowGroups = schedule.reduce((acc, block) => {
    if (!acc[block.window_id]) {
      acc[block.window_id] = [];
    }
    acc[block.window_id].push(block);
    return acc;
  }, {});

  const windowNames = {
    "WIN-W1-TUE": { day: "Tuesday", slot: "01:30 - 04:30 (180 min)", type: "Midweek Night Window" },
    "WIN-W2-THU": { day: "Thursday", slot: "02:00 - 05:00 (180 min)", type: "Midweek Freight Divert Slot" },
    "WIN-W3-SAT": { day: "Saturday", slot: "01:00 - 04:30 (210 min)", type: "Weekend Extended Block" },
    "WIN-W4-SUN": { day: "Sunday", slot: "01:00 - 05:00 (240 min)", type: "Major Sunday Integrated Block" },
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
      {/* Header & CP-SAT Stats */}
      <div className="flex flex-wrap items-center justify-between mb-4 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            <h3 className="font-bold text-base text-white">CP-SAT Weekly Block Allocation Plan</h3>
          </div>
          <p className="text-xs text-slate-400">
            Globally optimized via Google OR-Tools constraint programming respecting timetable, safety and resources
          </p>
        </div>

        {/* Solver Stats Pills */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-blue-950 text-blue-300 border border-blue-800 flex items-center space-x-1 font-semibold">
            <Cpu className="w-3.5 h-3.5" />
            <span>Solver: {stats?.status || "OPTIMAL"}</span>
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center space-x-1 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Scheduled: {schedule.length} Tasks</span>
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-purple-950 text-purple-300 border border-purple-800 flex items-center space-x-1 font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Bundled: {stats?.bundled_count || 0}</span>
          </span>
        </div>
      </div>

      {/* Windows Columns / Rows */}
      <div className="space-y-4">
        {Object.entries(windowNames).map(([winId, meta]) => {
          const tasksInWindow = windowGroups[winId] || [];

          return (
            <div key={winId} className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              {/* Window Header */}
              <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800/80">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-sm">{meta.day}</span>
                  <span className="text-xs text-blue-400 font-mono font-medium">{meta.slot}</span>
                  <span className="text-[11px] text-slate-400 hidden sm:inline">• {meta.type}</span>
                </div>
                <span className="text-xs font-semibold text-slate-300 bg-slate-800 px-2 py-0.5 rounded">
                  {tasksInWindow.length} allocated tasks
                </span>
              </div>

              {/* Tasks Cards inside this Window */}
              {tasksInWindow.length === 0 ? (
                <div className="text-xs text-slate-400 py-3 text-center italic">
                  No maintenance scheduled in this window
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {tasksInWindow.map((b) => (
                    <div
                      key={b.task_id}
                      className={`p-3 rounded-lg border flex flex-col justify-between ${
                        b.is_bundled
                          ? "bg-indigo-950/30 border-indigo-500/40"
                          : "bg-slate-900 border-slate-800"
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="font-bold text-white text-xs">{b.task_id}</span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                            b.status === "APPROVED" ? "bg-emerald-900 text-emerald-300" :
                            b.status === "OVERRIDDEN" ? "bg-amber-900 text-amber-300" :
                            "bg-slate-800 text-slate-300"
                          }`}>
                            {b.status}
                          </span>
                        </div>

                        <div className="text-xs font-medium text-slate-300 capitalize">
                          {b.work_type.replace(/_/g, " ")}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          KM {b.km_from} - {b.km_to} ({b.department})
                        </div>

                        {b.is_bundled && (
                          <div className="mt-2 text-[10px] text-indigo-300 bg-indigo-900/40 px-2 py-1 rounded border border-indigo-800/60 flex items-center space-x-1">
                            <Sparkles className="w-3 h-3 text-indigo-400 flex-shrink-0" />
                            <span>Auto-Shadow Bundled with <strong>{b.bundled_with}</strong></span>
                          </div>
                        )}
                      </div>

                      {/* Officer Decision Trigger */}
                      <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between">
                        <span className="text-[10px] text-slate-400">P: {b.priority_score}</span>
                        <button
                          onClick={() => onOfficerAction(b)}
                          className="flex items-center space-x-1 text-xs text-blue-400 hover:text-blue-300 font-semibold hover:underline"
                        >
                          <UserCheck className="w-3.5 h-3.5" />
                          <span>Officer Review</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
