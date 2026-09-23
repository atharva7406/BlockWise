import React from 'react';
import { X, HelpCircle, CheckCircle2, ShieldCheck, Scale, Cpu, Database } from 'lucide-react';

export default function HonestyPointsModal({ onClose }) {
  const qaPoints = [
    {
      q: "Is this ML trained on real data?",
      a: "No — no real historical railway failure dataset exists for a student hackathon team to train on. The prototype uses a transparent, explainable mathematical formula in place of trained black-box models, designed so real historical telemetry can be dropped in later to train models M1–M5 without altering the architecture.",
      icon: <Database className="w-5 h-5 text-blue-400" />,
      badge: "Honesty / Explainability",
    },
    {
      q: "How would you get real department data?",
      a: "The architecture adheres to the exact same canonical contract and adapters — in a production railway division, we simply swap the 'synthetic' mode tag for authorized railway API/export mode (TMS, SMMS, TDMS, COA); zero architecture or schema changes required.",
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
      badge: "Production Integration",
    },
    {
      q: "What stops the AI from making an unsafe call?",
      a: "Hard railway safety constraints live strictly outside the ML/scoring layer in deterministic safety gates and the CP-SAT constraint solver. The prioritization model never touches isolation rules, train spacing, or machinery collisions. Furthermore, zero autonomous block issuance is permitted — the human operating officer always makes the statutory decision.",
      icon: <ShieldCheck className="w-5 h-5 text-red-400" />,
      badge: "Absolute Safety Guarantee",
    },
    {
      q: "What happens when the model doesn't know?",
      a: "Confidence is shown separately from priority and is NEVER multiplied in. When telemetry is stale or conflicted, confidence drops visually and triggers a human officer review flag, rather than silently applying a hidden numerical discount to priority.",
      icon: <Scale className="w-5 h-5 text-amber-400" />,
      badge: "Epistemic Uncertainty",
    },
    {
      q: "Why this stack, not an LLM or a simpler heuristic?",
      a: "Google OR-Tools CP-SAT provides a mathematically provable feasibility guarantee for train safety constraints that probabilistic LLMs cannot offer. Every component (FastAPI, Pydantic, Pandas, OR-Tools, PostgreSQL, React) is open-source, modular, and containerized with Docker Compose to scale seamlessly from laptop demo to production.",
      icon: <Cpu className="w-5 h-5 text-purple-400" />,
      badge: "Mathematical Feasibility vs Hallucination",
    },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-3xl max-h-[85vh] rounded-2xl p-6 shadow-2xl flex flex-col relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-4 flex-shrink-0">
          <div className="p-2.5 rounded-xl bg-purple-600/20 text-purple-400 border border-purple-500/30">
            <HelpCircle className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Judge Q&A & Honesty Talking Points</h2>
            <p className="text-xs text-slate-400">
              Blueprint §13 guidelines for defensible, transparent answers during live presentation
            </p>
          </div>
        </div>

        {/* Q&A Cards List */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {qaPoints.map((item, idx) => (
            <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {item.icon}
                  <h3 className="font-bold text-sm text-white">{item.q}</h3>
                </div>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {item.badge}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed pl-7">
                {item.a}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
