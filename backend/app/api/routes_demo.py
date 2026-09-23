from fastapi import APIRouter
from ..services.block_planner import planner_service

router = APIRouter(prefix="/api/demo", tags=["Demo Simulations"])


@router.post("/emergency")
def simulate_emergency():
    """Simulates an urgent broken rail / track fracture event mid-demo."""
    emergency_task = planner_service.simulate_emergency_injection()
    return {
        "status": "EMERGENCY_INJECTED",
        "task": emergency_task,
        "message": "Emergency task inserted and schedule automatically re-solved for forward windows.",
    }


@router.post("/toggle-tdms")
def toggle_tdms_telemetry():
    """Simulates TDMS telemetry latency/loss to demonstrate the Data Health Gate handling STALE data."""
    return planner_service.toggle_tdms_stale()


@router.post("/reset")
def reset_demo():
    """Resets tasks and schedule back to initial demo state."""
    planner_service.initialize_state()
    return {"status": "RESET_COMPLETE"}
