from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.schema import (
    MaintenanceTask,
    BlockWindow,
    ScheduledBlock,
    BundleEvaluation,
    OfficerActionRequest,
    SourceMetadata,
)
from ..models.enums import HealthState, PolicyMode, Severity, BlockType, SourceMode, Department
from ..generator.synthetic_data import generate_synthetic_tasks
from ..core.health_gate import evaluate_task_health
from ..core.priority import calculate_priority_score
from ..core.bundler import evaluate_bundle_pair
from ..core.scheduler import generate_optimal_schedule


class BlockPlannerService:
    """
    Central orchestration service for the PS-27 Automatic Block Planning prototype.
    Maintains active system state (tasks, available block windows, generated schedule, officer audit log).
    """

    def __init__(self):
        self.policy_mode: PolicyMode = PolicyMode.BALANCED
        self.tdms_online: bool = True
        self.tasks: List[MaintenanceTask] = []
        self.windows: List[BlockWindow] = []
        self.schedule: List[ScheduledBlock] = []
        self.officer_audit_log: List[Dict[str, Any]] = []
        self.initialize_state()

    def initialize_state(self):
        # 1. Load initial synthetic tasks
        self.tasks = generate_synthetic_tasks()
        
        # 2. Setup standard weekly block windows for C-01 corridor (COA timetable slots)
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

    def recompute_pipeline(self):
        """Runs health gate, priority scoring, and bundle analysis across all tasks."""
        for t in self.tasks:
            evaluate_task_health(t)
            calculate_priority_score(t, self.policy_mode)

    def set_policy_mode(self, mode: PolicyMode):
        self.policy_mode = mode
        self.recompute_pipeline()
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

    def solve_schedule(self) -> Dict[str, Any]:
        """Runs CP-SAT solver and stores the generated weekly block plan."""
        self.recompute_pipeline()
        scheduled_blocks, stats = generate_optimal_schedule(self.tasks, self.windows)
        self.schedule = scheduled_blocks
        return {
            "stats": stats,
            "schedule": self.schedule,
        }

    def record_officer_action(self, req: OfficerActionRequest) -> Dict[str, Any]:
        """Human-in-the-loop: logs officer approval or override with mandatory reason."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": req.task_id,
            "action": req.action,
            "officer_id": req.officer_id,
            "mandatory_reason": req.mandatory_reason,
            "notes": req.notes,
        }
        self.officer_audit_log.append(audit_entry)

        # Update status in schedule if present
        for block in self.schedule:
            if block.task_id == req.task_id:
                block.status = "APPROVED" if req.action == "APPROVE" else "OVERRIDDEN"

        return {"status": "RECORDED", "entry": audit_entry}

    def simulate_emergency_injection(self) -> MaintenanceTask:
        """
        Live Demo Feature:
        Injects a sudden high-severity emergency broken rail / rail fracture task.
        Immediately re-runs scoring and CP-SAT to reschedule forward windows.
        """
        emergency_task = MaintenanceTask(
            task_id=f"EMG-{len(self.tasks) + 1}",
            department=Department.ENGG,
            asset_id="TRK-FRACTURE-141",
            corridor="C-01",
            km_from=141.2,
            km_to=141.2,
            work_type="rail_fracture_emergency_clamp",
            severity=Severity.CRITICAL,
            overdue_days=30,
            time_to_required_by_hrs=2.0,
            est_duration_min=90,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["ENGG-RAPID-RESPONSE"],
            equipment=["PORTABLE-WELDER"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(
                source="TMS-ALARM",
                mode=SourceMode.SYNTHETIC,
                last_sync="Just now",
                confidence=0.99,
            ),
        )
        self.tasks.insert(0, emergency_task)
        self.recompute_pipeline()
        self.solve_schedule()
        return emergency_task

    def toggle_tdms_stale(self) -> Dict[str, Any]:
        """
        Live Demo Feature:
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
                    t.health_reason = "Passed integrity, schema and telemetry checks"
                    t.confidence_score = 0.94

        self.recompute_pipeline()
        return {
            "tdms_online": self.tdms_online,
            "message": "TDMS status updated successfully",
        }


# Singleton instance
planner_service = BlockPlannerService()
