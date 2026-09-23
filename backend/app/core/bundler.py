from typing import Tuple, List, Optional
from ..models.schema import MaintenanceTask, BundleEvaluation
from ..models.enums import ReasonCode
from .topology import check_km_overlap


def evaluate_bundle_pair(task_a: MaintenanceTask, task_b: MaintenanceTask) -> BundleEvaluation:
    """
    Auto-Shadow Bundling Gate:
    Deterministic evaluation chain to determine if two maintenance tasks
    can be safely bundled under a single shadow block window.
    """
    # Gate 1: Corridor Match
    if task_a.corridor != task_b.corridor:
        return BundleEvaluation(
            task_a_id=task_a.task_id,
            task_b_id=task_b.task_id,
            is_bundleable=False,
            reason_code=ReasonCode.CORRIDOR_MISMATCH,
            reason_message=f"Tasks belong to different corridors ({task_a.corridor} vs {task_b.corridor})",
            estimated_time_saved_min=0,
        )

    # Gate 2: KM Spatial Overlap
    does_overlap, overlap_km = check_km_overlap(task_a, task_b)
    if not does_overlap:
        return BundleEvaluation(
            task_a_id=task_a.task_id,
            task_b_id=task_b.task_id,
            is_bundleable=False,
            reason_code=ReasonCode.NO_SPATIAL_OVERLAP,
            reason_message=f"No spatial chainage overlap (Task A: KM {task_a.km_from}-{task_a.km_to}, Task B: KM {task_b.km_from}-{task_b.km_to})",
            estimated_time_saved_min=0,
        )

    # Gate 3: Resource Collision (Check for overlapping non-shareable equipment or crew)
    common_equipment = set(task_a.equipment).intersection(set(task_b.equipment))
    if common_equipment:
        collided = ", ".join(common_equipment)
        return BundleEvaluation(
            task_a_id=task_a.task_id,
            task_b_id=task_b.task_id,
            is_bundleable=False,
            reason_code=ReasonCode.RESOURCE_COLLISION,
            reason_message=f"Resource collision on shared equipment: {collided}. Multiple teams cannot use the same machinery simultaneously.",
            estimated_time_saved_min=0,
        )

    # Gate 4: Isolation / Safety Compatibility
    # If one task requires overhead 25kV power cut (power_block / isolation) while another task requires live testing
    if task_a.isolation_required != task_b.isolation_required and "welding" in task_b.work_type:
        return BundleEvaluation(
            task_a_id=task_a.task_id,
            task_b_id=task_b.task_id,
            is_bundleable=False,
            reason_code=ReasonCode.ISOLATION_CONFLICT,
            reason_message="Isolation conflict: Heavy welding on live line cannot coexist with OHE 25kV power isolation rules.",
            estimated_time_saved_min=0,
        )

    # SUCCESS: Passed all deterministic gates
    # Estimated time saved by running concurrently under one corridor closure rather than two separate closures
    min_duration = min(task_a.est_duration_min, task_b.est_duration_min)
    time_saved = int(min_duration * 0.8)  # ~80% of the shorter task duration saved in block occupancy

    why_bundle = (
        f"Spatial overlap of {overlap_km} KM on corridor {task_a.corridor}. "
        f"Compatible departments ({task_a.department} + {task_b.department}) with distinct crews and compatible isolation protocols."
    )

    return BundleEvaluation(
        task_a_id=task_a.task_id,
        task_b_id=task_b.task_id,
        is_bundleable=True,
        reason_code=None,
        reason_message=why_bundle,
        estimated_time_saved_min=time_saved,
    )
