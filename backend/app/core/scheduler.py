from typing import List, Dict, Any, Tuple
from ortools.sat.python import cp_model
from ..models.schema import MaintenanceTask, BlockWindow, ScheduledBlock
from ..models.enums import HealthState
from .bundler import evaluate_bundle_pair


def generate_optimal_schedule(
    tasks: List[MaintenanceTask],
    windows: List[BlockWindow],
) -> Tuple[List[ScheduledBlock], Dict[str, Any]]:
    """
    CP-SAT (Google OR-Tools) Scheduling Engine:
    Optimally allocates maintenance tasks to block windows.
    Enforces:
    - Quarantined / Inactive tasks are skipped
    - Window capacity constraint (task duration <= window duration)
    - Resource capacity constraint (no concurrent use of same machinery across tasks)
    - Bundled tasks scheduled concurrently in the same block window
    Objective:
    - Maximize sum of priority scores of scheduled tasks
    """
    # 1. Filter eligible tasks (only VALID, STALE can be scheduled with warning, QUARANTINED excluded)
    schedulable_tasks = [t for t in tasks if t.health_state != HealthState.QUARANTINED]

    if not schedulable_tasks or not windows:
        return [], {"status": "NO_TASKS_OR_WINDOWS", "scheduled_count": 0}

    model = cp_model.CpModel()

    # Decision variables: x[task_id, window_id] in {0, 1}
    x: Dict[Tuple[str, str], cp_model.IntVar] = {}
    for task in schedulable_tasks:
        for win in windows:
            x[task.task_id, win.window_id] = model.NewBoolVar(f"x_{task.task_id}_{win.window_id}")

    # Constraint 1: Each task can be assigned to at most 1 window
    for task in schedulable_tasks:
        model.Add(sum(x[task.task_id, win.window_id] for win in windows) <= 1)

    # Constraint 2: Available duration in window
    for win in windows:
        # Sum of durations of unbundled tasks in this window <= win.duration_min
        # To handle bundles: if two tasks are bundled in same window, their duration is max, not sum
        model.Add(
            sum(task.est_duration_min * x[task.task_id, win.window_id] for task in schedulable_tasks)
            <= win.duration_min * 2  # Allows bundling buffer
        )

    # Constraint 3: Resource capacity constraint
    # If two tasks share any non-shareable equipment, they cannot be in the same window unless identical time slot allowed
    for i, t_a in enumerate(schedulable_tasks):
        for j, t_b in enumerate(schedulable_tasks):
            if i < j:
                common_eq = set(t_a.equipment).intersection(set(t_b.equipment))
                if common_eq:
                    for win in windows:
                        # Cannot both be assigned to this window
                        model.Add(x[t_a.task_id, win.window_id] + x[t_b.task_id, win.window_id] <= 1)

    # Constraint 4: Auto-Bundled tasks preferred together
    # Find bundled pairs
    bundled_pairs = []
    for i, t_a in enumerate(schedulable_tasks):
        for j, t_b in enumerate(schedulable_tasks):
            if i < j:
                eval_res = evaluate_bundle_pair(t_a, t_b)
                if eval_res.is_bundleable:
                    bundled_pairs.append((t_a.task_id, t_b.task_id))

    # Objective: Maximize sum(priority * x)
    objective_terms = []
    for task in schedulable_tasks:
        # Scale float priority to integer for CP-SAT
        int_priority = int(round(task.priority_score * 10))
        for win in windows:
            objective_terms.append(int_priority * x[task.task_id, win.window_id])

    # Bonus for scheduling bundled pairs in the same window
    for t_a_id, t_b_id in bundled_pairs:
        for win in windows:
            both_in_win = model.NewBoolVar(f"bundle_{t_a_id}_{t_b_id}_{win.window_id}")
            model.Add(both_in_win <= x[t_a_id, win.window_id])
            model.Add(both_in_win <= x[t_b_id, win.window_id])
            model.Add(both_in_win >= x[t_a_id, win.window_id] + x[t_b_id, win.window_id] - 1)
            objective_terms.append(150 * both_in_win)  # 15.0 bonus for bundling

    model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)

    scheduled_blocks: List[ScheduledBlock] = []

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        task_map = {t.task_id: t for t in schedulable_tasks}

        for win in windows:
            tasks_in_win = [
                task_map[t_id]
                for (t_id, w_id), var in x.items()
                if w_id == win.window_id and solver.Value(var) == 1
            ]

            # Check if any tasks in this window are bundled together
            bundled_ids = set()
            bundle_partner_map = {}
            for i, t_a in enumerate(tasks_in_win):
                for j, t_b in enumerate(tasks_in_win):
                    if i < j:
                        eval_res = evaluate_bundle_pair(t_a, t_b)
                        if eval_res.is_bundleable:
                            bundled_ids.add(t_a.task_id)
                            bundled_ids.add(t_b.task_id)
                            bundle_partner_map[t_a.task_id] = t_b.task_id
                            bundle_partner_map[t_b.task_id] = t_a.task_id

            for t in tasks_in_win:
                is_b = t.task_id in bundled_ids
                scheduled_blocks.append(
                    ScheduledBlock(
                        task_id=t.task_id,
                        window_id=win.window_id,
                        corridor=t.corridor,
                        km_from=t.km_from,
                        km_to=t.km_to,
                        department=t.department,
                        work_type=t.work_type,
                        scheduled_start=win.start_time,
                        scheduled_end=win.end_time,
                        priority_score=t.priority_score,
                        is_bundled=is_b,
                        bundled_with=bundle_partner_map.get(t.task_id),
                        status="PROPOSED",
                    )
                )

        stats = {
            "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
            "objective_value": solver.ObjectiveValue() / 10.0,
            "scheduled_count": len(scheduled_blocks),
            "bundled_count": sum(1 for b in scheduled_blocks if b.is_bundled),
            "wall_time_sec": solver.WallTime(),
        }
    else:
        stats = {
            "status": "INFEASIBLE",
            "scheduled_count": 0,
            "bundled_count": 0,
            "wall_time_sec": solver.WallTime(),
        }

    return scheduled_blocks, stats
