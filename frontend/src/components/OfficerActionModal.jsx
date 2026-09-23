import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle, AlertOctagon, UserCheck } from 'lucide-react';

export default function OfficerActionModal({ block, onClose, onSubmit }) {
  const [action, setAction] = useState("APPROVE"); // APPROVE, OVERRIDE
  const [officerId, setOfficerId] = useState("OFFICER-DIV-04");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!block) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason.trim()) {
      alert("A mandatory justification reason is required for safety compliance.");
      return;
    }
    setSubmitting(true);
    await onSubmit({
      task_id: block.task_id,
      action,
      officer_id: officerId,
      mandatory_reason: reason,
      notes,
    });
    setSubmitting(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-lg rounded-2xl p-6 shadow-2xl relative">
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
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Railway Operating Officer Decision</h2>
            <p className="text-xs text-slate-400">
              Statutory human-in-the-loop authorization under General & Subsidiary Rules (G&SR)
            </p>
          </div>
        </div>

        {/* Selected Block Info */}
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 mb-4 text-xs space-y-1">
          <div className="flex justify-between">
            <span className="text-slate-400">Task Reference:</span>
            <span className="font-bold text-white">{block.task_id} ({block.department})</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Operation:</span>
            <span className="text-slate-200 capitalize">{block.work_type.replace(/_/g, " ")}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Chainage Window:</span>
            <span className="text-slate-200">Corridor {block.corridor} | KM {block.km_from} - {block.km_to}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Scheduled Time Slot:</span>
            <span className="text-blue-400 font-semibold">{block.scheduled_start} - {block.scheduled_end}</span>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Action Toggle */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Decision Action:
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setAction("APPROVE")}
                className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 border transition-all ${
                  action === "APPROVE"
                    ? "bg-emerald-600/20 text-emerald-300 border-emerald-500 shadow-sm"
                    : "bg-slate-950 text-slate-400 border-slate-800 hover:text-white"
                }`}
              >
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span>Approve Block Order</span>
              </button>
              <button
                type="button"
                onClick={() => setAction("OVERRIDE")}
                className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 border transition-all ${
                  action === "OVERRIDE"
                    ? "bg-amber-600/20 text-amber-300 border-amber-500 shadow-sm"
                    : "bg-slate-950 text-slate-400 border-slate-800 hover:text-white"
                }`}
              >
                <AlertOctagon className="w-4 h-4 text-amber-400" />
                <span>Override Allocation</span>
              </button>
            </div>
          </div>

          {/* Officer ID */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Officer Credentials / Token:
            </label>
            <input
              type="text"
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          {/* Mandatory Reason */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Mandatory Justification Reason <span className="text-red-400">*</span>:
            </label>
            <textarea
              rows={2}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Verified sectional traction isolation clearance and freight path availability."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-blue-500 resize-none"
              required
            />
          </div>

          {/* Submit Button */}
          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className={`px-4 py-2 rounded-xl text-xs font-bold text-white transition-all shadow-md ${
                action === "APPROVE" ? "bg-emerald-600 hover:bg-emerald-500" : "bg-amber-600 hover:bg-amber-500"
              }`}
            >
              {submitting ? "Signing..." : `Confirm ${action === "APPROVE" ? "Approval" : "Override"}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
