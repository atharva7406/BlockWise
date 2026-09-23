const API_BASE = "http://localhost:8000/api";

export const fetchTasks = async (status = null) => {
  const url = status ? `${API_BASE}/tasks?status=${status}` : `${API_BASE}/tasks`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
};

export const setPolicyMode = async (mode) => {
  const res = await fetch(`${API_BASE}/tasks/policy-mode?mode=${encodeURIComponent(mode)}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to update policy mode");
  return res.json();
};

export const fetchBundles = async () => {
  const res = await fetch(`${API_BASE}/bundles`);
  if (!res.ok) throw new Error("Failed to fetch bundles");
  return res.json();
};

export const fetchSchedule = async () => {
  const res = await fetch(`${API_BASE}/schedule`);
  if (!res.ok) throw new Error("Failed to fetch schedule");
  return res.json();
};

export const solveSchedule = async () => {
  const res = await fetch(`${API_BASE}/schedule/solve`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to solve schedule");
  return res.json();
};

export const submitOfficerAction = async (payload) => {
  const res = await fetch(`${API_BASE}/schedule/officer-action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to record officer action");
  return res.json();
};

export const triggerEmergency = async () => {
  const res = await fetch(`${API_BASE}/demo/emergency`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger emergency simulation");
  return res.json();
};

export const toggleTdms = async () => {
  const res = await fetch(`${API_BASE}/demo/toggle-tdms`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to toggle TDMS state");
  return res.json();
};

export const resetDemo = async () => {
  const res = await fetch(`${API_BASE}/demo/reset`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset demo");
  return res.json();
};

// Canonical Contracts & Safeguards API
export const fetchCanonicalSchemas = async () => {
  const res = await fetch(`${API_BASE}/contracts/schemas`);
  if (!res.ok) throw new Error("Failed to fetch schemas");
  return res.json();
};

export const fetchTopologyMap = async () => {
  const res = await fetch(`${API_BASE}/contracts/topology`);
  if (!res.ok) throw new Error("Failed to fetch topology");
  return res.json();
};

export const fetchTrains = async () => {
  const res = await fetch(`${API_BASE}/contracts/trains`);
  if (!res.ok) throw new Error("Failed to fetch trains");
  return res.json();
};

export const fetchAssets = async () => {
  const res = await fetch(`${API_BASE}/contracts/assets`);
  if (!res.ok) throw new Error("Failed to fetch assets");
  return res.json();
};

export const fetchCertificates = async () => {
  const res = await fetch(`${API_BASE}/contracts/certificates`);
  if (!res.ok) throw new Error("Failed to fetch certificates");
  return res.json();
};

export const fetchSafeguards = async () => {
  const res = await fetch(`${API_BASE}/contracts/safeguards`);
  if (!res.ok) throw new Error("Failed to fetch safeguards");
  return res.json();
};
