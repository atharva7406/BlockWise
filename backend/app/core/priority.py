import math
from typing import Dict
from ..models.schema import MaintenanceTask
from ..models.enums import PolicyMode, Severity

WEIGHT_PROFILES: Dict[PolicyMode, Dict[str, float]] = {
    PolicyMode.SAFETY_FIRST: {"wR": 0.50, "wI": 0.35, "wT": 0.15},
    PolicyMode.BALANCED: {"wR": 0.40, "wI": 0.35, "wT": 0.25},
    PolicyMode.THROUGHPUT_FIRST: {"wR": 0.30, "wI": 0.35, "wT": 0.35},
}

SEVERITY_RISK_MAP = {
    Severity.CRITICAL: 1.0,
    Severity.HIGH: 0.80,
    Severity.MEDIUM: 0.50,
    Severity.LOW: 0.20,
}


def calculate_priority_score(
    task: MaintenanceTask,
    policy_mode: PolicyMode = PolicyMode.BALANCED,
    d_cap: float = 20.0,
    k: float = 0.03,
) -> MaintenanceTask:
    """
    Computes transparent R (Risk), I (Impact), and T (Time pressure) indicators
    and combines them into a 0-100 Priority score based on the active Policy Mode.
    Confidence is computed separately and NEVER multiplied into priority.
    """
    # 1. Risk indicator R [0, 1]
    base_r = SEVERITY_RISK_MAP.get(task.severity, 0.4)
    # Factor in isolation / equipment hazards
    r_val = min(1.0, base_r + (0.1 if task.isolation_required else 0.0))

    # 2. Operational Impact indicator I [0, 1]
    # In corridor C-01 (heavy trunk route), traffic impact scales with duration and department
    duration_factor = min(1.0, task.est_duration_min / 180.0)
    i_val = round(0.40 + (0.45 * duration_factor), 2)

    # 3. Time pressure indicator T [0, 1]
    t_overdue = min(task.overdue_days / d_cap, 1.0)
    hours_left = task.time_to_required_by_hrs if task.time_to_required_by_hrs is not None else 48.0
    t_deadline = math.exp(-k * max(0.0, hours_left))
    t_val = round(max(t_overdue, t_deadline), 2)

    # Weights
    weights = WEIGHT_PROFILES.get(policy_mode, WEIGHT_PROFILES[PolicyMode.BALANCED])
    wR = weights["wR"]
    wI = weights["wI"]
    wT = weights["wT"]

    # Priority 0-100
    priority = round(100.0 * (wR * r_val + wI * i_val + wT * t_val), 1)

    task.r_risk = round(r_val, 2)
    task.i_impact = round(i_val, 2)
    task.t_time = round(t_val, 2)
    task.priority_score = priority

    return task
