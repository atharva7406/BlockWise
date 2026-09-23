# PS-27 / SIH26027 — Automatic Block Planning Prototype

> **ML predicts → deterministic rules validate → CP-SAT proves feasibility → the officer decides → reality feeds learning.**

This repository contains the prototype build for **PS-27 / SIH26027: Automatic Maintenance Block Planning and Auto-Shadow Bundling**, structured according to [PS27_Prototype_Blueprint.md](file:///c:/Users/pmata/Desktop/hackathon/NationalSIH26/PS27_Prototype_Blueprint.md).

---

## Architecture Overview

```text
[Synthetic Data Generator] ──► 15-25 realistic multi-department records (C-01 corridor)
        │
        ▼
[Data Health Gate] ─────────► VALID / STALE / CONFLICTED / QUARANTINED state machine
        │
        ▼
[Topology Resolver] ────────► KM chainage normalization & spatial overlap detection
        │
        ▼
[Priority Engine] ──────────► Transparent R, I, T formula + policy modes (Safety/Balanced/Throughput)
        │
        ▼
[Auto-Shadow Gate] ─────────► Deterministic candidate bundling (WHY BUNDLE vs WHY NOT reason codes)
        │
        ▼
[CP-SAT Scheduler] ─────────► Google OR-Tools constraint satisfaction weekly block allocation
        │
        ▼
[Officer Console] ──────────► React UI with Approve / Override statutory decision logging
```

---

## Directory Structure

```text
NationalSIH26/
├── PS27_Prototype_Blueprint.md     # Architecture & build blueprint
├── README.md                       # Setup and run instructions
├── run_backend.bat                 # Fast one-click launch for FastAPI
├── run_frontend.bat                # Fast one-click launch for Vite React UI
├── backend/
│   ├── requirements.txt            # FastAPI, OR-Tools, Pandas, Pydantic
│   ├── venv/                       # Python 3.12 virtual environment
│   ├── main.py                     # FastAPI entrypoint with CORS & API routers
│   └── app/
│       ├── models/
│       │   ├── enums.py            # Department, HealthState, PolicyMode, ReasonCode
│       │   └── schema.py           # Canonical data models (Task, Window, ScheduledBlock)
│       ├── core/
│       │   ├── health_gate.py      # Data Health Gate state machine
│       │   ├── topology.py         # KM chainage resolver & spatial overlap
│       │   ├── priority.py         # Transparent R, I, T formula & policy weighting
│       │   ├── bundler.py          # Auto-Shadow Bundling Gate & reason codes
│       │   └── scheduler.py        # Google OR-Tools CP-SAT constraint scheduler
│       ├── generator/
│       │   └── synthetic_data.py   # Realistic synthetic corridor C-01 dataset
│       ├── api/
│       │   ├── routes_tasks.py     # Task registry & policy mode switching
│       │   ├── routes_bundles.py   # Auto-shadow bundling evaluations
│       │   ├── routes_schedule.py  # CP-SAT solve & officer review endpoints
│       │   └── routes_demo.py      # Emergency injection & TDMS stale simulation
│       └── services/
│           └── block_planner.py    # Master service orchestrator
└── frontend/
    ├── package.json                # React 19, Vite, Tailwind, Lucide, Recharts
    ├── vite.config.js              # Vite + Tailwind CSS plugin
    └── src/
        ├── App.jsx                 # Master application layout & navigation
        ├── components/
        │   ├── Navbar.jsx          # Brand, corridor selector & policy mode toggle
        │   ├── DemoControlBar.jsx  # Live demo controls (emergency, stale simulation)
        │   ├── TopologyView.jsx    # Visual KM chainage timeline with stacked tracks
        │   ├── TaskListView.jsx    # Health state filtering (VALID/STALE/CONFLICTED/QUARANTINED)
        │   ├── PriorityBreakdownView.jsx # Transparent R, I, T metrics & separate confidence
        │   ├── BundleView.jsx      # WHY BUNDLE vs WHY NOT reason codes
        │   ├── ScheduleGanttView.jsx # CP-SAT weekly timetable schedule
        │   └── OfficerActionModal.jsx # Statutory human officer sign-off & reason log
        └── services/
            └── api.js              # REST client for backend communication
```

---

## Quick Start Instructions

### 1. Launch Backend API
Open a terminal in the project root:
```powershell
.\run_backend.bat
```
*(Or directly activate virtual environment and start uvicorn:)*
```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```
- API Documentation (Swagger): `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

### 2. Launch Frontend Console
Open a second terminal in the project root:
```powershell
.\run_frontend.bat
```
*(Or directly run npm dev inside frontend:)*
```powershell
cd frontend
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## Key Features & Demo Beats

1. **Deterministic Auto-Shadow Bundling**: Outputs both **WHY BUNDLE** (with saved corridor minutes) and **WHY NOT** (explicit reason codes like `RESOURCE_COLLISION`, `ISOLATION_CONFLICT`, `NO_SPATIAL_OVERLAP`).
2. **Transparent Priority vs. Confidence**: Computes $R$ (Risk), $I$ (Impact), and $T$ (Time pressure) indicators based on selectable policy modes (*Safety-First*, *Balanced*, *Throughput-First*). Never multiplies Priority $\times$ Confidence.
3. **Data Health Gate**: Handles edge cases gracefully by classifying records as `VALID`, `STALE`, `CONFLICTED`, or `QUARANTINED`.
4. **Google OR-Tools CP-SAT Engine**: Provably optimal block allocation respecting non-overlapping corridor windows, machine constraints, and bundled task slots.
5. **Human-in-the-Loop Statutory Officer Console**: Zero autonomous block issuance; every block decision requires a human operating officer review with mandatory justification logging.
6. **Live Demo Triggers**: "Simulate Rail Fracture (Emergency Injection)" and "Toggle TDMS Telemetry Outage (Stale Data)" buttons for live judge presentations.
