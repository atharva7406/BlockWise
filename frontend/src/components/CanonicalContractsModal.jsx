import React, { useState, useEffect } from 'react';
import { X, FileCode2, ShieldAlert, Train, Database, CheckCircle2, Layers } from 'lucide-react';
import { fetchCanonicalSchemas, fetchTrains, fetchAssets, fetchSafeguards } from '../services/api';

export default function CanonicalContractsModal({ onClose }) {
  const [activeTab, setActiveTab] = useState("schemas"); // schemas, safeguards, trains, assets
  const [schemas, setSchemas] = useState({});
  const [selectedSchemaKey, setSelectedSchemaKey] = useState("MaintenanceTask");
  const [trains, setTrains] = useState([]);
  const [assets, setAssets] = useState([]);
  const [safeguardInfo, setSafeguardInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadContractsData() {
      try {
        const [schemaData, trainData, assetData, safeguardData] = await Promise.all([
          fetchCanonicalSchemas(),
          fetchTrains(),
          fetchAssets(),
          fetchSafeguards(),
        ]);
        setSchemas(schemaData);
        setTrains(trainData);
        setAssets(assetData);
        setSafeguardInfo(safeguardData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadContractsData();
  }, []);

  const schemaEntities = [
    { key: "MaintenanceTask", label: "MaintenanceTask (Core Work Entity)" },
    { key: "Asset", label: "Asset (Physical Infrastructure)" },
    { key: "Train", label: "Train (COA Timetable Schedule)" },
    { key: "BlockWindow", label: "BlockWindow (Available Track Slot)" },
    { key: "SourceMetadata", label: "SourceMetadata (3-Mode Tagging)" },
    { key: "TopologyMap", label: "TopologyMap (Corridor Chainage)" },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-4xl h-[85vh] rounded-2xl p-6 shadow-2xl flex flex-col relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-4 flex-shrink-0">
          <div className="p-2.5 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <FileCode2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-white">Canonical Data Contracts & Gate 0 Enforcement</h2>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-semibold">
                Pydantic v2 Validated
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Matches Technology Stack Report architecture: 6 canonical entities, Gate 0 quarantine, and DB constraints
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 space-x-2 mb-4 flex-shrink-0">
          <button
            onClick={() => setActiveTab("schemas")}
            className={`px-4 py-2 text-xs font-bold rounded-t-lg transition-all ${
              activeTab === "schemas"
                ? "bg-slate-800 text-blue-400 border-b-2 border-blue-500"
                : "text-slate-400 hover:text-white"
            }`}
          >
            1. Pydantic v2 Schemas (6 Entities)
          </button>
          <button
            onClick={() => setActiveTab("safeguards")}
            className={`px-4 py-2 text-xs font-bold rounded-t-lg transition-all ${
              activeTab === "safeguards"
                ? "bg-slate-800 text-amber-400 border-b-2 border-amber-500"
                : "text-slate-400 hover:text-white"
            }`}
          >
            2. DB Safety Constraint (Mode Tagging)
          </button>
          <button
            onClick={() => setActiveTab("trains")}
            className={`px-4 py-2 text-xs font-bold rounded-t-lg transition-all ${
              activeTab === "trains"
                ? "bg-slate-800 text-emerald-400 border-b-2 border-emerald-500"
                : "text-slate-400 hover:text-white"
            }`}
          >
            3. Corridor C-01 Trains ({trains.length})
          </button>
          <button
            onClick={() => setActiveTab("assets")}
            className={`px-4 py-2 text-xs font-bold rounded-t-lg transition-all ${
              activeTab === "assets"
                ? "bg-slate-800 text-purple-400 border-b-2 border-purple-500"
                : "text-slate-400 hover:text-white"
            }`}
          >
            4. Registered Assets ({assets.length})
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto pr-1">
          {activeTab === "schemas" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
              {/* Entity Picker */}
              <div className="space-y-1.5 bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-xs font-bold uppercase text-slate-400 tracking-wider block mb-2">
                  Canonical Models
                </span>
                {schemaEntities.map((ent) => (
                  <button
                    key={ent.key}
                    onClick={() => setSelectedSchemaKey(ent.key)}
                    className={`w-full text-left p-2.5 rounded-lg text-xs font-semibold transition-all ${
                      selectedSchemaKey === ent.key
                        ? "bg-blue-600 text-white shadow-sm"
                        : "text-slate-400 hover:text-white hover:bg-slate-900"
                    }`}
                  >
                    {ent.label}
                  </button>
                ))}
              </div>

              {/* Schema JSON Viewer */}
              <div className="md:col-span-2 bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col h-full overflow-hidden">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                  <span className="text-xs font-bold text-white font-mono">{selectedSchemaKey}.json</span>
                  <span className="text-[10px] text-slate-500">Auto-generated by Pydantic v2 model_json_schema()</span>
                </div>
                <pre className="flex-1 overflow-auto text-[11px] font-mono text-emerald-400 bg-slate-900/60 p-3 rounded-lg leading-relaxed border border-slate-800/80">
                  {JSON.stringify(schemas[selectedSchemaKey] || {}, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {activeTab === "safeguards" && (
            <div className="space-y-4">
              <div className="bg-amber-950/30 border border-amber-500/40 p-4 rounded-xl">
                <div className="flex items-center space-x-2 text-amber-300 font-bold text-sm mb-1">
                  <ShieldAlert className="w-5 h-5 text-amber-400" />
                  <span>Production Safeguard Constraint Enforced in Database DDL</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  To satisfy the Technology Stack Report safeguard requirement, records tagged with{" "}
                  <code className="text-amber-300">mode = "synthetic"</code> are strictly prevented from ever entering
                  or being scheduled in production tables.
                </p>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Database Constraint Name:</span>
                  <span className="font-mono font-bold text-white bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    {safeguardInfo?.safeguard_name || "ck_prevent_synthetic_in_prod"}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">SQL DDL Definition:</span>
                  <span className="font-mono font-bold text-amber-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    {safeguardInfo?.constraint_definition || "CHECK (is_production = FALSE OR mode != 'synthetic')"}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Enforcement Layer:</span>
                  <span className="text-slate-200">{safeguardInfo?.enforced_in}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Audit Storage Mechanism:</span>
                  <span className="text-emerald-400 font-medium">Relational columns + exact raw payload kept in JSONB column</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === "trains" && (
            <div className="space-y-2">
              <div className="text-xs text-slate-400 mb-2">
                Timetable trains operating across Corridor C-01 with speed-restriction sensitivities:
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {trains.map((tr) => (
                  <div key={tr.train_no} className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-white text-xs">{tr.train_no} - {tr.train_name}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        tr.train_type === "VANDE_BHARAT" ? "bg-blue-900 text-blue-200" :
                        tr.train_type === "RAJDHANI" ? "bg-red-900 text-red-200" :
                        tr.train_type === "EXPRESS" ? "bg-amber-900 text-amber-200" : "bg-slate-800 text-slate-300"
                      }`}>
                        {tr.train_type}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Route: {tr.origin} → {tr.destination} | Slot: {tr.scheduled_departure} - {tr.scheduled_arrival}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      Speed Sensitive: {tr.speed_restriction_sensitive ? "YES (P1 Priority)" : "NO"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "assets" && (
            <div className="space-y-2">
              <div className="text-xs text-slate-400 mb-2">
                Physical railway assets registered along Corridor C-01 chainage (KM 100 - 160):
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {assets.map((as) => (
                  <div key={as.asset_id} className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                    <div>
                      <div className="font-bold text-white text-xs">{as.asset_id}</div>
                      <div className="text-[11px] text-slate-400 capitalize">{as.asset_type.replace(/_/g, " ")} ({as.department})</div>
                      <div className="text-[10px] text-slate-500">KM {as.km_from} - {as.km_to}</div>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      as.status === "OPERATIONAL" ? "bg-emerald-950 text-emerald-300 border border-emerald-800" :
                      "bg-amber-950 text-amber-300 border border-amber-800"
                    }`}>
                      {as.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
