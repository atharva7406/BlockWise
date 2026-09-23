from typing import Tuple, List, Dict, Any
import pandas as pd
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


def calculate_corridor_overlap_matrix(tasks: List[MaintenanceTask]) -> pd.DataFrame:
    """
    Pandas-Powered KM Overlap Matrix (Blueprint §4):
    Converts maintenance tasks into a Pandas DataFrame and computes a pairwise
    spatial overlap matrix across corridor chainage coordinates.
    """
    if not tasks:
        return pd.DataFrame()

    records = [
        {
            "task_id": t.task_id,
            "department": t.department.value if hasattr(t.department, "value") else str(t.department),
            "km_start": min(t.km_from, t.km_to),
            "km_end": max(t.km_from, t.km_to),
        }
        for t in tasks
    ]
    df = pd.DataFrame(records)

    # Cross join using Pandas to compute spatial overlap
    df_cross = df.merge(df, how="cross", suffixes=("_a", "_b"))
    df_cross = df_cross[df_cross["task_id_a"] < df_cross["task_id_b"]]

    # Overlap interval: max(start_a, start_b) to min(end_a, end_b)
    df_cross["overlap_start"] = df_cross[["km_start_a", "km_start_b"]].max(axis=1)
    df_cross["overlap_end"] = df_cross[["km_end_a", "km_end_b"]].min(axis=1)
    df_cross["overlap_km"] = (df_cross["overlap_end"] - df_cross["overlap_start"]).clip(lower=0.0).round(2)
    df_cross["has_overlap"] = df_cross["overlap_km"] > 0

    return df_cross


def normalize_coordinates(raw_val: float, unit: str = "km") -> float:
    """
    Normalizes mixed unit inputs (e.g. metres to kilometres)
    """
    if unit.lower() in ["m", "meter", "meters", "metre", "metres"]:
        return round(raw_val / 1000.0, 3)
    return round(raw_val, 3)
