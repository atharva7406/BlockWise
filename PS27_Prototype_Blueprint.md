# PS-27 / SIH26027 — Automatic Block Planning
## Prototype Build Blueprint

This is the practical, buildable version of the full Phase 1–6 architecture. It scopes what to actually build for a hackathon prototype round, in what order, with what tech, and where to deliberately draw the line between "real working system" and "explained but not built."

---

## 1. Guiding Principle

> **ML predicts → deterministic rules validate → CP-SAT proves feasibility → the officer decides → reality feeds learning.**

Nothing in the prototype should violate this chain. Even where a component is simplified or faked for the demo, it must **behave** like the real pipeline (i.e., a rule-based stand-in for a model is fine; a hardcoded "optimal" schedule that ignores constraints is not).

**Zero autonomous block issuance.** Every demo path ends at an officer approval screen, never at an auto-executed action.

---

## 2. Scope Decision — What Gets Built vs. Explained

| Layer | Build for real | Explain only (slide/Q&A) |
|---|---|---|
| Data ingestion | Synthetic data generator, 3-mode contract (API/export/synthetic) tagging | Real TMS/SMMS/TDMS/COA API integration |
| Canonical schema + topology | Full working KM-chainage resolver, overlap confidence labeling | — |
| Data health gate | VALID / STALE / CONFLICTED / QUARANTINED state machine | — |
| Risk & Priority scoring | Rule-based / lightly-fitted transparent formula (R, I, T → 0–100) with explanation breakdown | Fully trained ML models (M1–M5) on real historical failure data |
| Confidence scoring | Simplified confidence formula (freshness + completeness) | Full calibration/OOD/cold-start statistical machinery |
| Auto-Shadow bundling | Deterministic gate chain (corridor→KM→time→work type→resources→dependencies→isolation) | — |
| Scheduling | CP-SAT (OR-Tools) with 2–3 hard constraints (no overlap, resource capacity, timetable windows) | Full soft-objective relaxation ladder (L0–L4) |
| Officer console | Working approve/override/why-this-task UI | Full audit spine, shift-handover briefs |
| Learning loop | Described only | Not built — no real outcome data exists yet |

---

## 3. System Architecture (Prototype Version)

```
[Synthetic Data Generator]
        │
        ▼
[Ingestion Adapters] ──► tag: API / export / synthetic
        │
        ▼
[Data Health Gate] ──► VALID / STALE / CONFLICTED / QUARANTINED
        │
        ▼
[Topology Resolver] ──► Corridor + KM range, overlap confidence
        │
        ▼
[Priority Engine] ──► R (risk), I (impact), T (time pressure) → 0–100 score + Confidence
        │
        ▼
[Auto-Shadow Gate] ──► candidate bundling, ACCEPT/REJECT + reason codes
        │
        ▼
[CP-SAT Scheduler] ──► weekly block plan, hard constraints enforced
        │
        ▼
[Officer Console] ──► Why-this-task / Why-bundle / Approve / Override
```

---

## 4. Tech Stack

- **Backend:** Python + FastAPI
- **Database:** PostgreSQL (+ PostGIS optional, or just numeric KM ranges — PostGIS is overkill for a 1D chainage system, plain float ranges are simpler and sufficient)
- **Scheduling:** Google OR-Tools (CP-SAT)
- **Scoring layer:** plain Python (weighted formula), pandas for feature prep — skip actual model training unless time allows; a well-designed transparent formula is *more* defensible in Q&A than a black-box model with no real training data anyway
- **Frontend:** React + Tailwind, a charting lib (Recharts) for the KM overlap timeline and priority breakdown
- **Data generation:** a Python script producing realistic messy synthetic records (see §6)
- **Deployment:** Docker Compose (single command demo spin-up — judges notice this)

---

## 5. Canonical Data Model

```json
{
  "task_id": "SNT-2211",
  "department": "S&T",
  "asset_id": "SIG-S42",
  "corridor": "C-01",
  "km_from": 140.7,
  "km_to": 140.7,
  "work_type": "signal_repair",
  "severity": "high",
  "overdue_days": 17,
  "est_duration_min": 60,
  "block_type": "traffic_block",
  "crew": ["SNT-C3"],
  "equipment": ["ME3"],
  "depends_on": [],
  "isolation_required": false,
  "source_meta": {
    "source": "TDMS",
    "mode": "synthetic",
    "last_sync": "14:32",
    "confidence": 0.94
  }
}
```

Core entities: `Asset`, `MaintenanceTask`, `Train`, `BlockWindow`, `SourceMetadata`, `TopologyMap`.

---

## 6. Synthetic Dataset Design (this is your "input problem is real" proof)

Build 15–25 tasks across one fictional corridor (`C-01`, KM 100–160), deliberately including:

- Tasks referenced by 3 different vocabularies (Track Section, OHE Elementary Section, Interlocking Group) that all resolve to the same KM range
- 1 point asset (e.g., a signal at KM 140.7) that overlaps a range asset (KM 140.0–141.5)
- 1 task with mixed units (metres vs KM) to show normalization
- 2–3 genuinely overlapping tasks from different departments (bundling candidates)
- 1 pair that overlaps spatially but has a resource/isolation conflict (rejected bundle — this is a strong demo beat)
- 1 stale record (`last_sync` > allowed threshold) → should show reduced confidence
- 1 conflicting record (COA says track free, TMS says occupied) → should show CONFLICTED state
- 1 record missing required fields → should show QUARANTINED, never scheduled
- A spread of overdue_days and severity so the priority ranking is visually meaningful

Tag every record `"mode": "synthetic"` — and be ready to say plainly in the demo that this stands in for TMS/SMMS/TDMS/COA, since production access doesn't exist for a student team.

---

## 7. Priority Formula (prototype version — transparent, not a trained model)

```
R = normalized risk indicator   (e.g., from severity + failure-history proxy)   [0,1]
I = normalized operational impact (traffic/route criticality proxy)             [0,1]
T = max(T_overdue, T_deadline)
    T_overdue  = min(overdue_days / D_cap, 1)
    T_deadline = exp(-k * time_to_required_by)   [0,1]

Priority = 100 × (wR·R + wI·I + wT·T)
```

Policy modes (selectable, same predictions underneath — only the weights change):

| Mode | wR | wI | wT |
|---|---|---|---|
| Safety-First | 0.50 | 0.35 | 0.15 |
| Balanced | 0.40 | 0.35 | 0.25 |
| Throughput-First | 0.30 | 0.35 | 0.35 |

**Never** compute `Priority × Confidence` — keep them as two separate displayed numbers. This single design choice is one of your strongest talking points; make sure the UI actually shows it that way.

Confidence (simplified for prototype):
```
C = min(C_data, C_model)
C_data  = f(source freshness, missing fields, conflict flag)
C_model = fixed conservative value if using rule-based scoring (be honest about this in Q&A)
```

---

## 8. Auto-Shadow Bundling Gate (deterministic — build this fully, it's cheap and visually strong)

Gate chain, all must pass:
`Corridor match → KM overlap → Time window overlap → Work-type compatibility → Crew/equipment availability → Dependency check → Isolation/safety compatibility`

Any single "NO" → tasks stay separate, output a reason code (`ISOLATION_CONFLICT`, `RESOURCE_COLLISION`, `SPATIAL`, etc.).

Output both:
- **WHY BUNDLE** (accept, with saved time estimate)
- **WHY NOT** (reject, with the specific reason)

This "why not" output is often skipped by competing teams and is an easy differentiator.

---

## 9. CP-SAT Scheduling (minimum viable version)

Decision variable: `x_task ∈ {0,1}` scheduled in this window, plus `start/end` per task.

**Hard constraints to actually implement:**
1. No two tasks overlap on the same corridor/line at the same time (unless successfully bundled)
2. Resource capacity (e.g., only 1 crane available at a time)
3. Tasks must fit inside COA-provided available block windows

**Objective:** maximize `Σ Priority_i × x_i` (schedule highest-priority work first, within constraints)

Skip for prototype: multi-day rolling horizon optimization, full soft-constraint relaxation ladder, schedule-stability penalties. Mention these exist in the full design.

---

## 10. Officer Console (UI) — Minimum Screens

1. **Task list view** — all synthetic tasks, department, corridor/KM, status (VALID/STALE/CONFLICTED/QUARANTINED)
2. **Topology view** — a simple horizontal timeline per corridor showing each department's KM range stacked, with overlaps highlighted (this is your best visual — build it early)
3. **Priority breakdown** — click a task → see R, I, T, Confidence, and the resulting score, plus policy-mode toggle
4. **Bundle view** — candidate bundles with WHY BUNDLE / WHY NOT
5. **Generated schedule** — Gantt-style weekly block plan output from CP-SAT
6. **Approve/Override screen** — officer can approve or override with a mandatory reason (even if it just logs to console/DB, don't skip this — it's the "human stays in control" proof)

---

## 11. Live Demo Script (pick ONE scripted edge case, make it bulletproof)

Recommended: **emergency task insertion mid-demo**

1. Show the normal state: task list, topology view, generated weekly schedule already approved
2. Inject a new high-severity emergency task via a "simulate emergency" button
3. Show it gets scored immediately (high priority, driven by severity + time pressure)
4. Show the schedule re-solving — only the affected forward window changes, already-locked/approved work stays frozen
5. Officer reviews and approves the updated plan

Alternative if time-constrained: **source outage / stale data**
1. Toggle "TDMS offline" 
2. Show confidence dropping on affected tasks, a STALE flag appearing, but the system continuing to operate on the last verified snapshot rather than failing

Practice this exact flow enough times that it can't break live.

---

## 12. Build Order / Timeline (suggested)

| Stage | Deliverable |
|---|---|
| 1 | Synthetic data generator + canonical schema + Postgres schema |
| 2 | Topology resolver (KM normalization, overlap detection, confidence labels) |
| 3 | Data health gate (VALID/STALE/CONFLICTED/QUARANTINED) |
| 4 | Priority formula + explanation breakdown |
| 5 | Auto-Shadow bundling gate + reason codes |
| 6 | CP-SAT scheduler with 2–3 hard constraints |
| 7 | React UI: task list + topology view (build this early, it demos well even half-finished) |
| 8 | React UI: priority breakdown, bundle view, schedule view |
| 9 | Officer approve/override screen |
| 10 | Wire the one scripted edge-case demo end-to-end |
| 11 | Docker Compose packaging, rehearse demo |

Build in this order because stages 1–3 are cheap, deterministic, and give you something demoable even if later stages run out of time — you'd rather have a rock-solid topology+data-health demo than a half-working scheduler.

---

## 13. Honesty Points for Q&A (prepare these answers)

- **"Is this ML trained on real data?"** → No — no real historical failure dataset exists for a student team to train on. The prototype uses a transparent, explainable formula in place of trained models, designed so real historical data can be dropped in later to train M1–M5 without changing the architecture.
- **"How would you get real department data?"** → Same canonical contract, same adapters — swap the synthetic mode for authorized API/export mode; no architecture change needed.
- **"What stops the AI from making an unsafe call?"** → Hard safety constraints live outside the ML/scoring layer, in the deterministic gates and CP-SAT — the model never touches isolation, dependency, or resource-conflict rules.
- **"What happens when the model doesn't know?"** → Confidence is shown separately from priority, never multiplied in; low confidence triggers a review flag, not a hidden priority discount.

---

## 14. What NOT to Build (explicitly out of scope for the demo)

- Real TMS/SMMS/TDMS/COA integration
- Trained ML models on real historical data
- Full P0 edge-case test suite (mention it exists; demo 1–2 cases live)
- Monthly-horizon scheduling (say "same engine, longer horizon")
- Urgency-inflation detector with real statistical calibration (a simple chart with synthetic data is enough)
- Full audit/governance spine, shift-handover briefs, override-rate monitoring

---

*One sentence for the pitch:* "We're not building an AI that guesses railway blocks — we're building a coordination and prioritization layer that knows when its data or prediction is uncertain, never bypasses hard safety rules, and gives the officer an explainable plan."
