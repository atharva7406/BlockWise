from typing import Tuple, List, Dict, Any
from ..models.schema import MaintenanceTask


def check_km_overlap(task_a: MaintenanceTask, task_b: MaintenanceTask, buffer_km: float = 0.1) -> Tuple[bool, float]:
    """
    Checks if two tasks overlap along the corridor chainage with an optional safety buffer.
    Returns: (does_overlap: bool, overlap_length_km: float)
    """
    if task_a.corridor != task_b.corridor:
        return False, 0.0

    start_a = min(task_a.km_from, task_a.km_to) - buffer_km
    end_a = max(task_a.km_from, task_a.km_to) + buffer_km
    start_b = min(task_b.km_from, task_b.km_to) - buffer_km
    end_b = max(task_b.km_from, task_b.km_to) + buffer_km

    overlap_start = max(start_a, start_b)
    overlap_end = min(end_a, end_b)

    if overlap_end >= overlap_start:
        overlap_len = round(overlap_end - overlap_start, 2)
        return True, overlap_len
    return False, 0.0


def normalize_coordinates(raw_val: float, unit: str = "km") -> float:
    """
    Normalizes mixed unit inputs (e.g. metres to kilometres)
    """
    if unit.lower() in ["m", "meter", "meters", "metre", "metres"]:
        return round(raw_val / 1000.0, 3)
    return round(raw_val, 3)
