from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..models.schema import MaintenanceTask
from ..models.enums import PolicyMode
from ..services.block_planner import planner_service

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=List[MaintenanceTask])
def get_all_tasks(status: Optional[str] = Query(None, description="Filter by VALID, STALE, CONFLICTED, QUARANTINED")):
    return planner_service.get_tasks(filter_status=status)


@router.get("/{task_id}", response_model=MaintenanceTask)
def get_task_by_id(task_id: str):
    tasks = planner_service.get_tasks()
    for t in tasks:
        if t.task_id == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/policy-mode")
def update_policy_mode(mode: PolicyMode):
    return planner_service.set_policy_mode(mode)
