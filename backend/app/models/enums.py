from enum import Enum


class Department(str, Enum):
    ENGG = "ENGG"      # Permanent Way / Track Engineering
    SNT = "S&T"        # Signals & Telecommunications
    OHE = "OHE"        # Overhead Equipment / Traction
    OPTG = "OPTG"      # Operating / Traffic


class HealthState(str, Enum):
    VALID = "VALID"
    STALE = "STALE"
    CONFLICTED = "CONFLICTED"
    QUARANTINED = "QUARANTINED"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PolicyMode(str, Enum):
    SAFETY_FIRST = "Safety-First"
    BALANCED = "Balanced"
    THROUGHPUT_FIRST = "Throughput-First"


class ReasonCode(str, Enum):
    CORRIDOR_MISMATCH = "CORRIDOR_MISMATCH"
    NO_SPATIAL_OVERLAP = "NO_SPATIAL_OVERLAP"
    TIME_WINDOW_MISMATCH = "TIME_WINDOW_MISMATCH"
    WORK_TYPE_INCOMPATIBLE = "WORK_TYPE_INCOMPATIBLE"
    RESOURCE_COLLISION = "RESOURCE_COLLISION"
    DEPENDENCY_VIOLATION = "DEPENDENCY_VIOLATION"
    ISOLATION_CONFLICT = "ISOLATION_CONFLICT"


class BlockType(str, Enum):
    TRAFFIC_BLOCK = "traffic_block"
    POWER_BLOCK = "power_block"
    INTEGRATED_BLOCK = "integrated_block"


class SourceMode(str, Enum):
    API = "API"
    EXPORT = "export"
    SYNTHETIC = "synthetic"
