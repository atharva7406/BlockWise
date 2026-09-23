from typing import Dict, Any, Union
from pydantic import ValidationError
from ..models.schema import MaintenanceTask, SourceMetadata
from ..models.enums import HealthState, Department, Severity, BlockType


def validate_gate0(raw_data: Dict[str, Any]) -> MaintenanceTask:
    """
    Gate 0 Strict Contract Validation (Blueprint §4):
    Every incoming record from adapters is parsed through the Pydantic v2 MaintenanceTask model.
    A record that fails contract validation is immediately quarantined BEFORE reaching the scoring engine.
    This guarantees that corrupt payloads never contaminate downstream priority and CP-SAT solvers.
    """
    try:
        task = MaintenanceTask(**raw_data)
        # If successfully validated against Pydantic, run health state machine
        return evaluate_task_health(task)
    except (ValidationError, Exception) as err:
        # Gate 0 caught schema violation -> isolate and quarantine
        error_details = str(err).split("\n")[0]
        fallback_task = MaintenanceTask(
            task_id=str(raw_data.get("task_id", "INVALID-TASK-ID")),
            department=Department.ENGG,
            asset_id=str(raw_data.get("asset_id", "UNVALIDATED_ASSET")),
            corridor=str(raw_data.get("corridor", "UNKNOWN")),
            km_from=-999.0,
            km_to=-999.0,
            work_type="contract_validation_failure",
            severity=Severity.LOW,
            health_state=HealthState.QUARANTINED,
            health_reason=f"Gate 0 Contract Violation: {error_details}",
            confidence_score=0.0,
        )
        return fallback_task


def evaluate_task_health(task: MaintenanceTask) -> MaintenanceTask:
    """
    Data Health Gate (Blueprint §2 & §3):
    State machine applying deterministic validation rules:
    - VALID: Passes schema, boundary checks, and active telemetry
    - STALE: High latency sync, low confidence data (e.g. TDMS offline)
    - CONFLICTED: Discrepancy between signaling (TMS) vs movement (COA)
    - QUARANTINED: Illegal KM range, missing asset, or schema violation (never scheduled)
    """
    # Check for Quarantine criteria (missing or illegal attributes)
    if task.km_from < 0 or task.km_to < 0 or task.km_from > 200:
        task.health_state = HealthState.QUARANTINED
        task.health_reason = f"Out-of-bounds KM chainage coordinates (KM {task.km_from} - {task.km_to})"
        task.confidence_score = 0.05
        return task

    if not task.asset_id or task.asset_id in ["UNKNOWN_ASSET", "UNVALIDATED_ASSET"]:
        task.health_state = HealthState.QUARANTINED
        task.health_reason = "Missing asset identifier or unmapped asset register"
        task.confidence_score = 0.10
        return task

    # Existing pre-flagged states (e.g., from telemetry adapters)
    if task.health_state == HealthState.CONFLICTED:
        task.confidence_score = 0.45
        return task

    if task.health_state == HealthState.STALE:
        task.confidence_score = 0.40
        return task

    # Default to VALID
    task.health_state = HealthState.VALID
    task.health_reason = "Passed Gate 0 validation, spatial boundary and telemetry checks"
    task.confidence_score = task.source_meta.confidence
    return task
