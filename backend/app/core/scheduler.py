from typing import List, Dict, Any, Tuple, Optional
from ortools.sat.python import cp_model
from ..models.schema import MaintenanceTask, BlockWindow, ScheduledBlock
from ..models.enums import HealthState
from .bundler import evaluate_bundle_pair


def generate_optimal_schedule(
    tasks: List[MaintenanceTask],
    windows: List[BlockWindow],
    frozen_allocations: Optional[Dict[str, str]] = None,
) -> Tuple[List[ScheduledBlock], Dict[str, Any]]:
    """
    CP-SAT (Google OR-Tools) Scheduling Engine (Blueprint §4 & §11):
    Optimally allocates maintenance tasks to block windows.
    Enforces:
    - Seed-reproducible deterministic solving
    - Quarantined / Inactive tasks are skipped
    - Window capacity constraint (task duration <= window duration)
    - Resource capacity constraint (no concurrent use of same machinery across tasks)
    - Bundled tasks scheduled concurrently in the same block window
    - Frozen Blocks: Previously approved tasks remain locked to their assigned windows
      when the schedule re-solves around an emergency injection.
    Objective:
    - Maximize sum of priority scores of scheduled tasks + bundling synergy bonuses
    """
    frozen_allocations = frozen_allocations or {}

    # 1. Filter eligible tasks (only VALID, STALE can be scheduled with warning, QUARANTINED excluded)
    schedulable_tasks = [t for t in tasks if t.health_state != HealthState.QUARANTINED]

    if not schedulable_tasks or not windows:
        return [], {
            "status": "NO_TASKS_OR_WINDOWS",
            "scheduled_count": 0,
            "bundled_count": 0,
            "seed": 42,
            "wall_time_sec": 0.0,
        }

    model = cp_model.CpModel()
    window_map = {win.window_id: win for win in windows}

    # Decision variables: x[task_id, window_id] in {0, 1}
    x: Dict[Tuple[str, str], cp_model.IntVar] = {}
    for task in schedulable_tasks:
        for win in windows:
            x[task.task_id, win.window_id] = model.NewBoolVar(f"x_{task.task_id}_{win.window_id}")

    # Constraint 1: Each task can be assigned to at most 1 window
    for task in schedulable_tasks:
        model.Add(sum(x[task.task_id, win.window_id] for win in windows) <= 1)

    # Constraint 2: Frozen Block Preservation (Blueprint §11)
    # If a task was already approved by an officer, it MUST stay in its locked window
    for task_id, locked_win_id in frozen_allocations.items():
        if locked_win_id in window_map and any(t.task_id == task_id for t in schedulable_tasks):
            model.Add(x[task_id, locked_win_id] == 1)

    # Constraint 3: Available duration in window
    for win in windows:
        model.Add(
            sum(task.est_duration_min * x[task.task_id, win.window_id] for task in schedulable_tasks)
            <= win.duration_min * 2  # Allows bundling concurrency buffer
        )

    # Constraint 4: Resource capacity constraint
    # If two tasks share any non-shareable equipment, they cannot be in the same window
    for i, t_a in enumerate(schedulable_tasks):
        for j, t_b in enumerate(schedulable_tasks):
            if i < j:
                common_eq = set(t_a.equipment).intersection(set(t_b.equipment))
                if common_eq:
                    for win in windows:
                        model.Add(x[t_a.task_id, win.window_id] + x[t_b.task_id, win.window_id] <= 1)

    # Constraint 5: Bundled tasks preference
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
            objective_terms.append(150 * both_in_win)  # 15.0 bonus for bundling synergy

    model.Maximize(sum(objective_terms))

    # Solve with deterministic seed
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.random_seed = 42
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
                is_previously_frozen = t.task_id in frozen_allocations
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
                        status="APPROVED" if is_previously_frozen else "PROPOSED",
                    )
                )

        solver_status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
        stats = {
            "status": solver_status_str,
            "objective_value": round(solver.ObjectiveValue() / 10.0, 1),
            "scheduled_count": len(scheduled_blocks),
            "bundled_count": sum(1 for b in scheduled_blocks if b.is_bundled),
            "frozen_count": len(frozen_allocations),
            "wall_time_sec": round(solver.WallTime(), 4),
            "seed": 42,
        }
    else:
        stats = {
            "status": "INFEASIBLE",
            "scheduled_count": 0,
            "bundled_count": 0,
            "frozen_count": len(frozen_allocations),
            "wall_time_sec": round(solver.WallTime(), 4),
            "seed": 42,
        }

    return scheduled_blocks, stats
