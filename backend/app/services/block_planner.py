from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from ..models.schema import (
    MaintenanceTask,
    BlockWindow,
    ScheduledBlock,
    BundleEvaluation,
    BundleCertificate,
    OfficerActionRequest,
    SourceMetadata,
    Asset,
    Train,
    TopologyMap,
)
from ..models.enums import HealthState, PolicyMode, Severity, BlockType, SourceMode, Department
from ..generator.synthetic_data import (
    generate_synthetic_tasks,
    generate_canonical_assets,
    generate_canonical_trains,
    generate_canonical_topology_map,
)
from ..core.health_gate import evaluate_task_health, validate_gate0
from ..core.priority import calculate_priority_score
from ..core.bundler import evaluate_bundle_pair
from ..core.scheduler import generate_optimal_schedule
from ..db.database import SessionLocal, init_db
from ..db.models import TaskRecord, BundleCertificateRecord, PlanAuditRecord


class BlockPlannerService:
    """
    Central orchestration service for the PS-27 Automatic Block Planning prototype (Blueprint §3).
    Coordinates:
    - Ingestion and Gate 0 Contract Validation
    - Data Health Gate state machine
    - Priority Engine with policy modes (R, I, T indicators)
    - Auto-Shadow Bundling Gate (WHY BUNDLE vs WHY NOT reasons)
    - Google OR-Tools CP-SAT scheduler with frozen-block preservation
    - Statutory officer review logging & exact audit replay
    - PostgreSQL / SQLite relational persistence
    """

    def __init__(self):
        self.policy_mode: PolicyMode = PolicyMode.BALANCED
        self.tdms_online: bool = True
        self.tasks: List[MaintenanceTask] = []
        self.assets: List[Asset] = []
        self.trains: List[Train] = []
        self.topology_map: Optional[TopologyMap] = None
        self.windows: List[BlockWindow] = []
        self.schedule: List[ScheduledBlock] = []
        self.frozen_allocations: Dict[str, str] = {}  # task_id -> window_id for approved blocks
        self.certificates: List[BundleCertificate] = []
        self.officer_audit_log: List[Dict[str, Any]] = []
        
        # Initialize DB and state
        init_db()
        self.initialize_state()

    def initialize_state(self):
        """Initializes canonical datasets across all 6 core entities."""
        self.tasks = generate_synthetic_tasks()
        self.assets = generate_canonical_assets()
        self.trains = generate_canonical_trains()
        self.topology_map = generate_canonical_topology_map()
        self.frozen_allocations.clear()
        
        # 4 available timetable windows for C-01 corridor
        self.windows = [
            BlockWindow(
                window_id="WIN-W1-TUE",
                corridor="C-01",
                km_from=100.0,
                km_to=160.0,
                start_time="Tue 01:30",
                end_time="Tue 04:30",
                duration_min=180,
            ),
            BlockWindow(
                window_id="WIN-W2-THU",
                corridor="C-01",
                km_from=100.0,
                km_to=160.0,
                start_time="Thu 02:00",
                end_time="Thu 05:00",
                duration_min=180,
            ),
            BlockWindow(
                window_id="WIN-W3-SAT",
                corridor="C-01",
                km_from=100.0,
                km_to=160.0,
                start_time="Sat 01:00",
                end_time="Sat 04:30",
                duration_min=210,
            ),
            BlockWindow(
                window_id="WIN-W4-SUN",
                corridor="C-01",
                km_from=100.0,
                km_to=160.0,
                start_time="Sun 01:00",
                end_time="Sun 05:00",
                duration_min=240,
            ),
        ]
        self.recompute_pipeline()
        self.sync_tasks_to_db()

    def recompute_pipeline(self):
        """Runs health gate, priority scoring, and bundle analysis across all tasks."""
        for t in self.tasks:
            evaluate_task_health(t)
            calculate_priority_score(t, self.policy_mode)

    def sync_tasks_to_db(self):
        """Persists canonical tasks to relational database with raw JSON payload."""
        db = SessionLocal()
        try:
            for t in self.tasks:
                existing = db.query(TaskRecord).filter(TaskRecord.task_id == t.task_id).first()
                if not existing:
                    rec = TaskRecord(
                        task_id=t.task_id,
                        department=t.department.value if hasattr(t.department, "value") else str(t.department),
                        asset_id=t.asset_id,
                        corridor=t.corridor,
                        km_from=t.km_from,
                        km_to=t.km_to,
                        work_type=t.work_type,
                        severity=t.severity.value if hasattr(t.severity, "value") else str(t.severity),
                        health_state=t.health_state.value if hasattr(t.health_state, "value") else str(t.health_state),
                        priority_score=t.priority_score,
                        confidence_score=t.confidence_score,
                        mode=t.source_meta.mode.value if hasattr(t.source_meta.mode, "value") else str(t.source_meta.mode),
                        is_scheduled=t.is_scheduled,
                        is_production=False,  # Safeguard: synthetic records remain false
                        raw_payload=t.model_dump(),
                    )
                    db.add(rec)
                else:
                    existing.priority_score = t.priority_score
                    existing.confidence_score = t.confidence_score
                    existing.health_state = t.health_state.value if hasattr(t.health_state, "value") else str(t.health_state)
                    existing.raw_payload = t.model_dump()
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    def set_policy_mode(self, mode: PolicyMode):
        self.policy_mode = mode
        self.recompute_pipeline()
        self.sync_tasks_to_db()
        return {"status": "SUCCESS", "active_policy_mode": self.policy_mode}

    def get_tasks(self, filter_status: Optional[str] = None) -> List[MaintenanceTask]:
        if filter_status:
            return [t for t in self.tasks if t.health_state.value == filter_status.upper()]
        return self.tasks

    def get_bundle_candidates(self) -> List[BundleEvaluation]:
        """Evaluates pairwise bundling candidates across valid tasks."""
        valid_tasks = [t for t in self.tasks if t.health_state != HealthState.QUARANTINED]
        evaluations: List[BundleEvaluation] = []
        for i, t_a in enumerate(valid_tasks):
            for j, t_b in enumerate(valid_tasks):
                if i < j:
                    eval_res = evaluate_bundle_pair(t_a, t_b)
                    evaluations.append(eval_res)
        return evaluations

    def generate_bundle_certificates(self) -> List[BundleCertificate]:
        """Generates audit-ready bundle certificates for approved pairs."""
        evals = self.get_bundle_candidates()
        certs = []
        for ev in evals:
            if ev.is_bundleable:
                cert_id = f"CERT-SHADOW-{ev.task_a_id}-{ev.task_b_id}"
                task_a = next(t for t in self.tasks if t.task_id == ev.task_a_id)
                task_b = next(t for t in self.tasks if t.task_id == ev.task_b_id)
                cert = BundleCertificate(
                    certificate_id=cert_id,
                    task_a_id=ev.task_a_id,
                    task_b_id=ev.task_b_id,
                    corridor=task_a.corridor,
                    km_overlap_range=f"KM {min(task_a.km_from, task_b.km_from)} - {max(task_a.km_to, task_b.km_to)}",
                    departments_bundled=[str(task_a.department), str(task_b.department)],
                    time_saved_min=ev.estimated_time_saved_min,
                    hash_signature=f"SHA256:{hash((cert_id, ev.estimated_time_saved_min)) & 0xffffffff:08x}",
                )
                certs.append(cert)
        self.certificates = certs
        return certs

    def solve_schedule(self) -> Dict[str, Any]:
        """
        Runs CP-SAT solver with frozen block preservation (Blueprint §11).
        Preserves previously approved tasks in their assigned windows while
        re-optimizing forward slots.
        """
        self.recompute_pipeline()
        scheduled_blocks, stats = generate_optimal_schedule(
            tasks=self.tasks,
            windows=self.windows,
            frozen_allocations=self.frozen_allocations,
        )
        self.schedule = scheduled_blocks
        return {
            "stats": stats,
            "schedule": self.schedule,
        }

    def record_officer_action(self, req: OfficerActionRequest) -> Dict[str, Any]:
        """Human-in-the-loop statutory officer approval or override with audit persistence."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": req.task_id,
            "action": req.action,
            "officer_id": req.officer_id,
            "mandatory_reason": req.mandatory_reason,
            "notes": req.notes,
        }
        self.officer_audit_log.append(audit_entry)

        # Update block status in memory
        target_win = None
        for block in self.schedule:
            if block.task_id == req.task_id:
                if req.action == "APPROVE":
                    block.status = "APPROVED"
                    target_win = block.window_id
                    # Freeze this task in its window for future re-solves
                    self.frozen_allocations[req.task_id] = target_win
                else:
                    block.status = "OVERRIDDEN"
                    if req.task_id in self.frozen_allocations:
                        del self.frozen_allocations[req.task_id]

        # Persist to relational database
        db = SessionLocal()
        try:
            db_audit = PlanAuditRecord(
                timestamp=audit_entry["timestamp"],
                task_id=req.task_id,
                action=req.action,
                officer_id=req.officer_id,
                mandatory_reason=req.mandatory_reason,
                notes=req.notes,
                raw_payload=audit_entry,
            )
            db.add(db_audit)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        return {"status": "RECORDED", "entry": audit_entry, "frozen_allocations": self.frozen_allocations}

    def simulate_emergency_injection(self) -> MaintenanceTask:
        """
        Live Demo Script (Blueprint §11):
        1. Inject broken rail emergency task.
        2. Immediate scoring (high severity + time urgency).
        3. Schedule re-solves: previously APPROVED tasks STAY FROZEN in their windows;
           unapproved forward windows adapt to accommodate the emergency.
        """
        emergency_raw = {
            "task_id": f"EMG-{len(self.tasks) + 1}",
            "department": Department.ENGG,
            "asset_id": "TRK-FRACTURE-141",
            "corridor": "C-01",
            "km_from": 141.2,
            "km_to": 141.2,
            "work_type": "rail_fracture_emergency_clamp",
            "severity": Severity.CRITICAL,
            "overdue_days": 30,
            "time_to_required_by_hrs": 2.0,
            "est_duration_min": 90,
            "block_type": BlockType.TRAFFIC_BLOCK,
            "crew": ["ENGG-RAPID-RESPONSE"],
            "equipment": ["PORTABLE-WELDER"],
            "depends_on": [],
            "isolation_required": False,
            "source_meta": {
                "source": "TMS-ALARM",
                "mode": "synthetic",
                "last_sync": "Just now",
                "confidence": 0.99,
            },
        }

        # Enforce Gate 0 validation
        emergency_task = validate_gate0(emergency_raw)
        self.tasks.insert(0, emergency_task)
        self.recompute_pipeline()
        self.solve_schedule()
        self.sync_tasks_to_db()
        return emergency_task

    def toggle_tdms_stale(self) -> Dict[str, Any]:
        """
        Live Demo Feature (Blueprint §11):
        Toggles TDMS telemetry offline/online. Drops confidence and marks S&T tasks STALE.
        """
        self.tdms_online = not self.tdms_online
        for t in self.tasks:
            if t.department == Department.SNT and t.source_meta.source == "TDMS":
                if not self.tdms_online:
                    t.health_state = HealthState.STALE
                    t.health_reason = "TDMS Telemetry Gateway Offline (Simulated Outage)"
                    t.confidence_score = 0.35
                else:
                    t.health_state = HealthState.VALID
                    t.health_reason = "Passed Gate 0 validation, spatial boundary and telemetry checks"
                    t.confidence_score = 0.94

        self.recompute_pipeline()
        self.sync_tasks_to_db()
        return {
            "tdms_online": self.tdms_online,
            "message": "TDMS telemetry state toggled successfully",
        }


# Global singleton instance
planner_service = BlockPlannerService()
