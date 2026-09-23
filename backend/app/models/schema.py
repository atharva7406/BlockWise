from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .enums import Department, HealthState, Severity, PolicyMode, ReasonCode, BlockType, SourceMode


class SourceMetadata(BaseModel):
    source: str = "TDMS"  # TMS, SMMS, TDMS, COA
    mode: SourceMode = SourceMode.SYNTHETIC
    last_sync: str = "14:32"
    confidence: float = 0.94


class MaintenanceTask(BaseModel):
    task_id: str
    department: Department
    asset_id: str
    corridor: str = "C-01"
    km_from: float
    km_to: float
    work_type: str
    severity: Severity = Severity.MEDIUM
    overdue_days: int = 0
    time_to_required_by_hrs: Optional[float] = 48.0
    est_duration_min: int = 60
    block_type: BlockType = BlockType.TRAFFIC_BLOCK
    crew: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    isolation_required: bool = False
    source_meta: SourceMetadata = Field(default_factory=SourceMetadata)

    # Computed fields by Health Gate, Topology & Priority Engine
    health_state: HealthState = HealthState.VALID
    health_reason: Optional[str] = None
    r_risk: float = 0.0
    i_impact: float = 0.0
    t_time: float = 0.0
    priority_score: float = 0.0
    confidence_score: float = 0.85
    is_scheduled: bool = False


class BundleEvaluation(BaseModel):
    task_a_id: str
    task_b_id: str
    is_bundleable: bool
    reason_code: Optional[ReasonCode] = None
    reason_message: str
    estimated_time_saved_min: int = 0


class BlockWindow(BaseModel):
    window_id: str
    corridor: str = "C-01"
    km_from: float = 100.0
    km_to: float = 160.0
    start_time: str
    end_time: str
    duration_min: int = 180


class ScheduledBlock(BaseModel):
    task_id: str
    window_id: str
    corridor: str
    km_from: float
    km_to: float
    department: Department
    work_type: str
    scheduled_start: str
    scheduled_end: str
    priority_score: float
    is_bundled: bool = False
    bundled_with: Optional[str] = None
    status: str = "PROPOSED"  # PROPOSED, APPROVED, OVERRIDDEN


class OfficerActionRequest(BaseModel):
    task_id: str
    action: str  # "APPROVE" or "OVERRIDE"
    officer_id: str
    mandatory_reason: str
    notes: Optional[str] = None
