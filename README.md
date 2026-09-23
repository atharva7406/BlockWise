# PS-27 / SIH26027 — Automatic Block Planning Prototype

> **ML predicts → deterministic rules validate → CP-SAT proves feasibility → the officer decides → reality feeds learning.**

This repository contains the prototype build for **PS-27 / SIH26027: Automatic Maintenance Block Planning and Auto-Shadow Bundling**, aligned with [PS27_Prototype_Blueprint_updated.md](file:///c:/Users/pmata/Desktop/hackathon/NationalSIH26/PS27_Prototype_Blueprint_updated.md) and the team's Technology Stack Report.

---

## Architecture Overview

```text
[Synthetic Data Generator] ──► 15-25 realistic multi-department records (C-01 corridor)
        │
        ▼
[Gate 0 Schema Validation] ──► Pydantic v2 strict contract validation; schema-invalid -> QUARANTINED
        │
        ▼
[Data Health Gate] ─────────► VALID / STALE / CONFLICTED / QUARANTINED state machine
        │
        ▼
[Topology Resolver] ────────► Pandas-powered KM chainage overlap joins & vocabulary normalization
        │
        ▼
[Priority Engine] ──────────► Transparent R, I, T formula + policy modes (Safety/Balanced/Throughput)
        │
        ▼
[Auto-Shadow Gate] ─────────► Deterministic candidate bundling (WHY BUNDLE vs WHY NOT reason codes)
        │
        ▼
[CP-SAT Scheduler] ─────────► Google OR-Tools (Seed 42) + Frozen Block Preservation for approved work
        │
        ▼
[Officer Console] ──────────► React UI with Approve / Override statutory decision logging
        │
        ▼
[Relational DB & Audit] ────► PostgreSQL/SQLite with JSONB exact audit replay + Synthetic-in-Prod DB constraint
```

---

## 6 Canonical Entities (Pydantic v2)

1. **`SourceMetadata`**: 3-mode tagging (`API`, `export`, `synthetic`), source identifier (`TMS`, `SMMS`, `TDMS`, `COA`), timestamp, and confidence score.
2. **`Asset`**: Physical infrastructure asset registry (track sections, color-light signals, point machines, OHE elementary sections) mapped to corridor chainage.
3. **`MaintenanceTask`**: Work demand record with department, chainage, work type, duration, crews, equipment, dependencies, and isolation requirement.
4. **`Train`**: Timetable train services (Vande Bharat, Rajdhani, Express, Freight) with speed-restriction sensitivities.
5. **`BlockWindow`**: Timetable slots provided by COA with affected tracks and duration limits.
6. **`TopologyMap`**: Corridor C-01 mapping normalizing 3 distinct departmental vocabularies (Track Sections, Interlocking Groups, OHE Elementary Sections) to unified KM chainage.

---

## Technology Stack Safeguards

- **Gate 0 Validation**: Any incoming record that fails Pydantic schema validation is automatically quarantined before reaching scoring.
- **Production Mode Safeguard**: Database check constraint `CHECK (is_production = FALSE OR mode != 'synthetic')` permanently prevents test/synthetic records from being marked schedulable in production.
- **Audit Replay**: Normalized relational tables store every attribute while preserving the exact raw JSON/JSONB payload for non-repudiation.
- **Frozen-Block Preservation**: When an emergency broken rail is injected mid-demo, already approved blocks remain strictly locked in their assigned windows (`x[task_id, original_win] == 1`), while forward windows adapt dynamically.
- **Mathematical Safety Guarantee**: Hard safety constraints (isolation, spatial collisions, equipment capacity) live exclusively outside the scoring layer in deterministic gates and CP-SAT.

---

## Quick Start Instructions

### Option 1: Native Local Run (Zero Setup)
1. **Backend**:
   ```powershell
   .\run_backend.bat
   ```
   API runs on `http://localhost:8000` (OpenAPI Swagger at `/docs`).
2. **Frontend**:
   ```powershell
   .\run_frontend.bat
   ```
   UI runs on `http://localhost:5173`.

### Option 2: Docker Compose (Full Stack)
```bash
docker-compose up --build
```
Spins up:
- `db`: PostgreSQL 16 on port 5432
- `backend`: FastAPI with Google OR-Tools on port 8000
- `frontend`: React Vite bundle served by Nginx on port 5173

---

## Live Demo Highlights

1. **Topology & Chainage Overlaps**: Stacked track view for ENGG, S&T, and OHE showing point signals vs range assets.
2. **Auto-Shadow Bundling Gate**: Evaluates candidate pairs and provides explicit **WHY BUNDLE** (with saved corridor minutes) and **WHY NOT** (`RESOURCE_COLLISION`, `ISOLATION_CONFLICT`, `NO_SPATIAL_OVERLAP`).
3. **Emergency Injection & Frozen Blocks**: Click "Simulate Rail Fracture" to inject an emergency event. Watch already-approved blocks stay `LOCKED / FROZEN` while unapproved blocks re-optimize forward.
4. **Data Contracts Modal**: Click "Data Contracts (Gate 0)" in the navbar to inspect all 6 canonical entity schemas and the DB check constraint.
5. **Judge Q&A Guide**: Click "Q&A Guide (§13)" in the navbar to view transparent, defensible talking points for judge presentations.
