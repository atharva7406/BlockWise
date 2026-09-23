import React, { useState } from 'react';
import { Layers, Info, MapPin } from 'lucide-react';

export default function TopologyView({ tasks, onSelectTask }) {
  const [hoveredTask, setHoveredTask] = useState(null);

  const CORRIDOR_START = 100.0;
  const CORRIDOR_END = 160.0;
  const CORRIDOR_LENGTH = CORRIDOR_END - CORRIDOR_START;

  const getPositionPercent = (km) => {
    const clamped = Math.max(CORRIDOR_START, Math.min(CORRIDOR_END, km));
    return ((clamped - CORRIDOR_START) / CORRIDOR_LENGTH) * 100;
  };

  const departments = [
    { id: "ENGG", label: "Track Engineering (ENGG)", color: "bg-amber-500", border: "border-amber-400" },
    { id: "S&T", label: "Signals & Telecom (S&T)", color: "bg-emerald-500", border: "border-emerald-400" },
    { id: "OHE", label: "Overhead Equipment (OHE)", color: "bg-purple-500", border: "border-purple-400" },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-blue-400" />
          <h3 className="font-bold text-base text-white">Corridor C-01 Spatial Topology & Chainage Overlaps</h3>
          <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            KM 100.0 → KM 160.0 (60 KM Trunk Route)
          </span>
        </div>
        <div className="flex items-center space-x-4 text-xs text-slate-400">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span>
            <span>ENGG</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
            <span>S&T</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block"></span>
            <span>OHE</span>
          </div>
          <div className="flex items-center space-x-1.5 text-blue-400 font-medium">
            <Info className="w-3.5 h-3.5" />
            <span>Click any block to inspect R, I, T priority</span>
          </div>
        </div>
      </div>

      {/* Corridor KM Ruler */}
      <div className="relative w-full h-8 mb-3 bg-slate-950/80 rounded-lg border border-slate-800 flex items-center px-2">
        {[100, 110, 120, 130, 140, 150, 160].map((km) => {
          const leftPercent = ((km - CORRIDOR_START) / CORRIDOR_LENGTH) * 100;
          return (
            <div
              key={km}
              className="absolute top-0 bottom-0 flex flex-col items-center justify-between py-1"
              style={{ left: `${leftPercent}%`, transform: 'translateX(-50%)' }}
            >
              <div className="w-0.5 h-2 bg-slate-600"></div>
              <span className="text-[10px] font-mono text-slate-400 font-semibold">{km}K</span>
            </div>
          );
        })}
      </div>

      {/* Department Tracks */}
      <div className="space-y-4 my-2">
        {departments.map((dept) => {
          const deptTasks = tasks.filter((t) => t.department === dept.id && t.health_state !== "QUARANTINED");

          return (
            <div key={dept.id} className="relative">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1 font-medium">
                <span>{dept.label}</span>
                <span>{deptTasks.length} tasks scheduled</span>
              </div>
              
              {/* Track line */}
              <div className="relative w-full h-10 bg-slate-950 rounded-xl border border-slate-800/80 overflow-hidden">
                {/* Background grid lines */}
                <div className="absolute inset-0 grid grid-cols-6 divide-x divide-slate-800/40 pointer-events-none">
                  <div></div><div></div><div></div><div></div><div></div><div></div>
                </div>

                {/* Render Task Blocks */}
                {deptTasks.map((t) => {
                  const left = getPositionPercent(Math.min(t.km_from, t.km_to));
                  const right = getPositionPercent(Math.max(t.km_from, t.km_to));
                  // Ensure minimum visible width for point assets (e.g. signals)
                  const width = Math.max(1.8, right - left);

                  const isHovered = hoveredTask?.task_id === t.task_id;

                  return (
                    <button
                      key={t.task_id}
                      onClick={() => onSelectTask(t)}
                      onMouseEnter={() => setHoveredTask(t)}
                      onMouseLeave={() => setHoveredTask(null)}
                      title={`${t.task_id} (${t.work_type}): KM ${t.km_from} - ${t.km_to}`}
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                      }}
                      className={`absolute top-1.5 bottom-1.5 rounded-md px-1 flex items-center justify-center text-[10px] font-bold text-white transition-all cursor-pointer shadow-md ${dept.color} ${
                        isHovered ? "ring-2 ring-white scale-105 z-20" : "opacity-90 hover:opacity-100"
                      }`}
                    >
                      <span className="truncate">{t.task_id}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Hovered Task Quick Peek */}
      {hoveredTask && (
        <div className="mt-3 p-3 bg-slate-800/80 border border-slate-700 rounded-xl flex items-center justify-between text-xs text-slate-300 animate-fadeIn">
          <div className="flex items-center space-x-3">
            <span className="font-bold text-white bg-slate-700 px-2 py-0.5 rounded">{hoveredTask.task_id}</span>
            <span>{hoveredTask.work_type.replace(/_/g, " ")}</span>
            <span className="text-slate-400">|</span>
            <span>KM {hoveredTask.km_from} - {hoveredTask.km_to}</span>
            <span className="text-slate-400">|</span>
            <span className="text-amber-400 font-semibold">Priority: {hoveredTask.priority_score}</span>
          </div>
          <div className="text-slate-400">Click card for complete R, I, T breakdown</div>
        </div>
      )}
    </div>
  );
}
