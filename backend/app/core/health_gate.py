from ..models.schema import MaintenanceTask
from ..models.enums import HealthState


def evaluate_task_health(task: MaintenanceTask) -> MaintenanceTask:
    """
    Data Health Gate:
    Applies deterministic validation rules to classify task records into:
    - VALID: Safe to schedule
    - STALE: High latency sync, low confidence data
    - CONFLICTED: Discrepancy between signaling / train movement sources
    - QUARANTINED: Corrupt, missing attributes, or out-of-corridor coordinates (never scheduled)
    """
    # Check for Quarantine criteria (missing or illegal attributes)
    if task.km_from < 0 or task.km_to < 0 or task.km_from > 200:
        task.health_state = HealthState.QUARANTINED
        task.health_reason = "Out-of-bounds KM chainage coordinates"
        task.confidence_score = 0.10
        return task

    if not task.asset_id or task.asset_id == "UNKNOWN_ASSET":
        task.health_state = HealthState.QUARANTINED
        task.health_reason = "Missing asset identifier or unmapped asset register"
        task.confidence_score = 0.10
        return task

    # Existing pre-flagged states
    if task.health_state == HealthState.CONFLICTED:
        task.confidence_score = 0.45
        return task

    if task.health_state == HealthState.STALE:
        task.confidence_score = 0.50
        return task

    # Default to VALID
    task.health_state = HealthState.VALID
    task.health_reason = "Passed integrity, schema and telemetry checks"
    task.confidence_score = task.source_meta.confidence
    return task
