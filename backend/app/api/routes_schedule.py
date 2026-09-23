from fastapi import APIRouter
from typing import Dict, Any, List
from ..models.schema import OfficerActionRequest
from ..services.block_planner import planner_service

router = APIRouter(prefix="/api/schedule", tags=["Schedule"])


@router.post("/solve")
def solve_schedule():
    """Triggers the CP-SAT engine to generate the weekly block plan."""
    return planner_service.solve_schedule()


@router.get("")
def get_current_schedule():
    """Gets the most recently generated schedule or generates one if empty."""
    if not planner_service.schedule:
        return planner_service.solve_schedule()
    return {
        "stats": {"status": "CACHED", "scheduled_count": len(planner_service.schedule)},
        "schedule": planner_service.schedule,
    }


@router.post("/officer-action")
def submit_officer_action(req: OfficerActionRequest):
    """Logs human officer approval or override with required reason."""
    return planner_service.record_officer_action(req)


@router.get("/audit-log")
def get_audit_log():
    return planner_service.officer_audit_log
