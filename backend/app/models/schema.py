from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .enums import Department, HealthState, Severity, PolicyMode, ReasonCode, BlockType, SourceMode


# 1. Canonical Entity: SourceMetadata
class SourceMetadata(BaseModel):
    source: str = "TDMS"  # TMS, SMMS, TDMS, COA
    mode: SourceMode = SourceMode.SYNTHETIC
    last_sync: str = "14:32"
    confidence: float = 0.94


# 2. Canonical Entity: Asset
class Asset(BaseModel):
    asset_id: str
    department: Department
    asset_type: str  # track_section, signal, point_machine, ohe_cantilever, substation
    corridor: str = "C-01"
    km_from: float
    km_to: float
    status: str = "OPERATIONAL"  # OPERATIONAL, DEGRADED, FAILED
    last_inspected: str = "2026-09-15"


# 3. Canonical Entity: MaintenanceTask
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


# 4. Canonical Entity: Train (Timetable entity affected by blocks)
class Train(BaseModel):
    train_no: str
    train_name: str
    train_type: str  # VANDE_BHARAT, RAJDHANI, EXPRESS, FREIGHT
    corridor: str = "C-01"
    origin: str
    destination: str
    scheduled_departure: str
    scheduled_arrival: str
    priority_level: int = 1  # 1 = highest (Vande Bharat/Rajdhani), 4 = Freight
    speed_restriction_sensitive: bool = True


# 5. Canonical Entity: BlockWindow (COA available timetable slots)
class BlockWindow(BaseModel):
    window_id: str
    corridor: str = "C-01"
    km_from: float = 100.0
    km_to: float = 160.0
    start_time: str
    end_time: str
    duration_min: int = 180
    tracks_affected: List[str] = Field(default_factory=lambda: ["UP", "DOWN"])


# 6. Canonical Entity: TopologyMap (Corridor chainage & multi-vocabulary mapping)
class TopologyMap(BaseModel):
    corridor_id: str = "C-01"
    corridor_name: str = "Northern Trunk High-Density Line (KM 100 - 160)"
    km_start: float = 100.0
    km_end: float = 160.0
    track_sections: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    interlocking_groups: Dict[str, float] = Field(default_factory=dict)
    ohe_elementary_sections: Dict[str, Dict[str, float]] = Field(default_factory=dict)


# Auto-Shadow Bundle Evaluation & Certificate
class BundleEvaluation(BaseModel):
    task_a_id: str
    task_b_id: str
    is_bundleable: bool
    reason_code: Optional[ReasonCode] = None
    reason_message: str
    estimated_time_saved_min: int = 0


class BundleCertificate(BaseModel):
    certificate_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    task_a_id: str
    task_b_id: str
    corridor: str
    km_overlap_range: str
    departments_bundled: List[str]
    time_saved_min: int
    authorized_by: str = "AUTO_SHADOW_ENGINE_G8"
    hash_signature: str = ""


# Schedule Output
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
    status: str = "PROPOSED"  # PROPOSED, APPROVED, OVERRIDDEN, FROZEN


# Officer Sign-off & Audit Replay Request
class OfficerActionRequest(BaseModel):
    task_id: str
    action: str  # "APPROVE" or "OVERRIDE"
    officer_id: str
    mandatory_reason: str
    notes: Optional[str] = None
