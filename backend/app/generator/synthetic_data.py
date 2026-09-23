"""
Synthetic Dataset Generator for PS-27 Automatic Block Planning Prototype (Blueprint §5 & §6).
Generates realistic canonical data across all 6 core entities:
1. SourceMetadata
2. Asset
3. MaintenanceTask
4. Train
5. BlockWindow
6. TopologyMap
Includes multi-department tasks, 3 vocabularies (Track Section, OHE Elementary Section, Interlocking Group),
point vs range assets, unit conversions, bundling pairs, isolation conflicts, stale telemetry, and quarantine cases.
"""

from typing import List, Dict, Any
from ..models.schema import (
    MaintenanceTask,
    SourceMetadata,
    Asset,
    Train,
    BlockWindow,
    TopologyMap,
)
from ..models.enums import Department, Severity, BlockType, SourceMode, HealthState


def generate_canonical_topology_map() -> TopologyMap:
    """
    Corridor C-01 Topology Map (Blueprint §6):
    Normalizes 3 distinct operational railway vocabularies to unified KM chainage:
    - Track Engineering: Track Sections (TRK-SEC)
    - Signals & Telecom: Interlocking Groups & Signals (INT-GRP, SIG)
    - Traction/Electrical: OHE Elementary Sections (OHE-ELEC)
    """
    return TopologyMap(
        corridor_id="C-01",
        corridor_name="Northern Heavy Trunk Line (KM 100.0 - 160.0)",
        km_start=100.0,
        km_end=160.0,
        track_sections={
            "TRK-SEC-12": {"km_from": 102.0, "km_to": 103.5},
            "TRK-SEC-28B": {"km_from": 115.0, "km_to": 118.0},
            "TRK-SEC-33A": {"km_from": 128.5, "km_to": 131.0},
            "TRK-SEC-42A": {"km_from": 140.0, "km_to": 141.5},
            "TRK-SEC-55C": {"km_from": 152.0, "km_to": 155.0},
            "TRK-SEC-58": {"km_from": 158.0, "km_to": 160.0},
        },
        interlocking_groups={
            "INT-GRP-08": 105.4,
            "SIG-S19": 122.3,
            "SIG-S42": 140.7,
            "SIG-S88": 156.2,
        },
        ohe_elementary_sections={
            "OHE-ELEC-115": {"km_from": 115.0, "km_to": 118.0},
            "OHE-ELEC-129": {"km_from": 128.5, "km_to": 131.0},
            "OHE-ELEC-148": {"km_from": 147.0, "km_to": 150.0},
        },
    )


def generate_canonical_assets() -> List[Asset]:
    """Generates canonical railway assets residing along Corridor C-01."""
    return [
        Asset(asset_id="TRK-SEC-12", department=Department.ENGG, asset_type="track_section", km_from=102.0, km_to=103.5, status="DEGRADED", last_inspected="2026-09-01"),
        Asset(asset_id="INT-GRP-08", department=Department.SNT, asset_type="interlocking_point", km_from=105.4, km_to=105.4, status="OPERATIONAL", last_inspected="2026-09-10"),
        Asset(asset_id="OHE-ELEC-115", department=Department.OHE, asset_type="catenary_wire", km_from=115.0, km_to=118.0, status="OPERATIONAL", last_inspected="2026-09-12"),
        Asset(asset_id="TRK-SEC-28B", department=Department.ENGG, asset_type="track_section", km_from=115.2, km_to=117.8, status="OPERATIONAL", last_inspected="2026-09-05"),
        Asset(asset_id="SIG-S19", department=Department.SNT, asset_type="color_light_signal", km_from=122.3, km_to=122.3, status="DEGRADED", last_inspected="2026-09-08"),
        Asset(asset_id="OHE-ELEC-129", department=Department.OHE, asset_type="tension_regulator", km_from=128.5, km_to=131.0, status="DEGRADED", last_inspected="2026-08-28"),
        Asset(asset_id="TRK-SEC-33A", department=Department.ENGG, asset_type="welded_joint", km_from=129.0, km_to=130.5, status="DEGRADED", last_inspected="2026-09-03"),
        Asset(asset_id="TRK-SEC-42A", department=Department.ENGG, asset_type="track_section", km_from=140.0, km_to=141.5, status="DEGRADED", last_inspected="2026-09-02"),
        Asset(asset_id="SIG-S42", department=Department.SNT, asset_type="auto_signal", km_from=140.7, km_to=140.7, status="DEGRADED", last_inspected="2026-09-14"),
        Asset(asset_id="OHE-ELEC-148", department=Department.OHE, asset_type="insulator_bank", km_from=147.0, km_to=150.0, status="OPERATIONAL", last_inspected="2026-09-15"),
        Asset(asset_id="TRK-SEC-55C", department=Department.OPTG, asset_type="speed_board", km_from=152.0, km_to=155.0, status="OPERATIONAL", last_inspected="2026-09-11"),
        Asset(asset_id="TRK-SEC-58", department=Department.ENGG, asset_type="ballast_bed", km_from=158.0, km_to=159.8, status="OPERATIONAL", last_inspected="2026-09-16"),
    ]


def generate_canonical_trains() -> List[Train]:
    """Generates scheduled train timetable profiles running on Corridor C-01."""
    return [
        Train(train_no="22436", train_name="Vande Bharat Express", train_type="VANDE_BHARAT", corridor="C-01", origin="NDLS", destination="BSB", scheduled_departure="06:00", scheduled_arrival="07:15", priority_level=1, speed_restriction_sensitive=True),
        Train(train_no="12302", train_name="Rajdhani Express", train_type="RAJDHANI", corridor="C-01", origin="NDLS", destination="HWH", scheduled_departure="16:50", scheduled_arrival="18:10", priority_level=1, speed_restriction_sensitive=True),
        Train(train_no="12424", train_name="Dibrugarh Rajdhani", train_type="RAJDHANI", corridor="C-01", origin="NDLS", destination="DBRG", scheduled_departure="20:30", scheduled_arrival="22:00", priority_level=1, speed_restriction_sensitive=True),
        Train(train_no="12876", train_name="Neelachal Superfast", train_type="EXPRESS", corridor="C-01", origin="ANVT", destination="PURI", scheduled_departure="07:30", scheduled_arrival="09:15", priority_level=2, speed_restriction_sensitive=False),
        Train(train_no="BTPN-902", train_name="POL Petroleum Freight Rake", train_type="FREIGHT", corridor="C-01", origin="IOC-SIDING", destination="DIV-YARD", scheduled_departure="01:15", scheduled_arrival="04:00", priority_level=4, speed_restriction_sensitive=False),
        Train(train_no="BOXN-441", train_name="Coal Rake Freight Special", train_type="FREIGHT", corridor="C-01", origin="COAL-DEPOT", destination="THERMAL-PWR", scheduled_departure="02:00", scheduled_arrival="05:30", priority_level=4, speed_restriction_sensitive=False),
    ]


def generate_synthetic_tasks() -> List[MaintenanceTask]:
    """
    Generates 13 multi-department maintenance tasks across Corridor C-01.
    All tagged mode: synthetic (Blueprint §6).
    """
    tasks = [
        # Bundle Candidate Pair 1: ENGG + S&T (KM 140.0 - 141.5, compatible)
        MaintenanceTask(
            task_id="ENG-101",
            department=Department.ENGG,
            asset_id="TRK-SEC-42A",
            corridor="C-01",
            km_from=140.0,
            km_to=141.5,
            work_type="rail_grinding",
            severity=Severity.HIGH,
            overdue_days=14,
            est_duration_min=90,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["ENGG-CREW-1"],
            equipment=["GRINDER-01"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TMS", mode=SourceMode.SYNTHETIC, last_sync="14:30", confidence=0.95),
        ),
        MaintenanceTask(
            task_id="SNT-201",
            department=Department.SNT,
            asset_id="SIG-S42",
            corridor="C-01",
            km_from=140.7,
            km_to=140.7,
            work_type="signal_repair",
            severity=Severity.HIGH,
            overdue_days=17,
            est_duration_min=60,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["SNT-CREW-A"],
            equipment=["TOOL-SNT"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TDMS", mode=SourceMode.SYNTHETIC, last_sync="14:32", confidence=0.94),
        ),

        # Bundle Candidate Pair 2: OHE + ENGG (KM 115.0 - 118.0, integrated block compatible)
        MaintenanceTask(
            task_id="OHE-301",
            department=Department.OHE,
            asset_id="OHE-ELEC-115",
            corridor="C-01",
            km_from=115.0,
            km_to=118.0,
            work_type="cantilever_inspection",
            severity=Severity.MEDIUM,
            overdue_days=5,
            est_duration_min=120,
            block_type=BlockType.POWER_BLOCK,
            crew=["OHE-TOWER-1"],
            equipment=["TOWER-WAGON-A"],
            depends_on=[],
            isolation_required=True,
            source_meta=SourceMetadata(source="SMMS", mode=SourceMode.SYNTHETIC, last_sync="14:20", confidence=0.92),
        ),
        MaintenanceTask(
            task_id="ENG-102",
            department=Department.ENGG,
            asset_id="TRK-SEC-28B",
            corridor="C-01",
            km_from=115.2,
            km_to=117.8,
            work_type="sleeper_fastener_check",
            severity=Severity.MEDIUM,
            overdue_days=8,
            est_duration_min=100,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["ENGG-CREW-2"],
            equipment=["HAND-GAUGE"],
            depends_on=[],
            isolation_required=True,
            source_meta=SourceMetadata(source="TMS", mode=SourceMode.SYNTHETIC, last_sync="14:25", confidence=0.90),
        ),

        # Overlapping Spatially but REJECTED BUNDLE (Isolation / Resource Collision Demo Beat)
        MaintenanceTask(
            task_id="OHE-302",
            department=Department.OHE,
            asset_id="OHE-ELEC-129",
            corridor="C-01",
            km_from=128.5,
            km_to=131.0,
            work_type="catenary_re-tensioning",
            severity=Severity.HIGH,
            overdue_days=12,
            est_duration_min=150,
            block_type=BlockType.POWER_BLOCK,
            crew=["OHE-TOWER-2"],
            equipment=["CRANE-X1"],
            depends_on=[],
            isolation_required=True,
            source_meta=SourceMetadata(source="SMMS", mode=SourceMode.SYNTHETIC, last_sync="14:15", confidence=0.91),
        ),
        MaintenanceTask(
            task_id="ENG-103",
            department=Department.ENGG,
            asset_id="TRK-SEC-33A",
            corridor="C-01",
            km_from=129.0,
            km_to=130.5,
            work_type="flash_butt_welding",
            severity=Severity.HIGH,
            overdue_days=10,
            est_duration_min=120,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["ENGG-CREW-HEAVY"],
            equipment=["CRANE-X1"],  # Collision on machinery
            depends_on=[],
            isolation_required=False, # Conflict on power isolation
            source_meta=SourceMetadata(source="TMS", mode=SourceMode.SYNTHETIC, last_sync="14:10", confidence=0.88),
        ),

        # Stale record edge case (reduced confidence)
        MaintenanceTask(
            task_id="SNT-202",
            department=Department.SNT,
            asset_id="INT-GRP-08",
            corridor="C-01",
            km_from=105.4,
            km_to=105.4,
            work_type="point_machine_testing",
            severity=Severity.MEDIUM,
            overdue_days=3,
            est_duration_min=45,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["SNT-CREW-B"],
            equipment=["MULTIMETER"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TDMS", mode=SourceMode.SYNTHETIC, last_sync="06:15", confidence=0.45),
            health_state=HealthState.STALE,
            health_reason="Last TDMS sync > 8 hours ago",
        ),

        # Conflicted record edge case
        MaintenanceTask(
            task_id="OPT-401",
            department=Department.OPTG,
            asset_id="TRK-SEC-55C",
            corridor="C-01",
            km_from=152.0,
            km_to=155.0,
            work_type="speed_restriction_removal",
            severity=Severity.HIGH,
            overdue_days=15,
            est_duration_min=60,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["OPT-INSP-1"],
            equipment=[],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="COA", mode=SourceMode.SYNTHETIC, last_sync="14:31", confidence=0.50),
            health_state=HealthState.CONFLICTED,
            health_reason="TMS track circuit reports active freight movement; COA reports idle",
        ),

        # Quarantined record (illegal KM chainage -> Gate 0 Quarantine)
        MaintenanceTask(
            task_id="ENG-999",
            department=Department.ENGG,
            asset_id="UNKNOWN_ASSET",
            corridor="C-01",
            km_from=-1.0,
            km_to=-1.0,
            work_type="corrupted_ballast_dump",
            severity=Severity.LOW,
            overdue_days=0,
            est_duration_min=0,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=[],
            equipment=[],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TMS", mode=SourceMode.SYNTHETIC, last_sync="14:33", confidence=0.10),
            health_state=HealthState.QUARANTINED,
            health_reason="Gate 0 violation: negative KM chainage coordinates & missing equipment crew list",
        ),

        # Additional tasks for priority ranking spread
        MaintenanceTask(
            task_id="ENG-104",
            department=Department.ENGG,
            asset_id="TRK-SEC-12",
            corridor="C-01",
            km_from=102.0,
            km_to=103.5,
            work_type="deep_screening",
            severity=Severity.CRITICAL,
            overdue_days=25,
            est_duration_min=180,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["ENGG-CREW-SPECIAL"],
            equipment=["BCM-MACHINE"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TMS", mode=SourceMode.SYNTHETIC, last_sync="14:30", confidence=0.96),
        ),
        MaintenanceTask(
            task_id="SNT-203",
            department=Department.SNT,
            asset_id="SIG-S19",
            corridor="C-01",
            km_from=122.3,
            km_to=122.3,
            work_type="axle_counter_calibration",
            severity=Severity.HIGH,
            overdue_days=19,
            est_duration_min=75,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["SNT-CREW-C"],
            equipment=["CALIBRATOR-PRO"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TDMS", mode=SourceMode.SYNTHETIC, last_sync="14:28", confidence=0.94),
        ),
        MaintenanceTask(
            task_id="OHE-303",
            department=Department.OHE,
            asset_id="OHE-ELEC-148",
            corridor="C-01",
            km_from=147.0,
            km_to=150.0,
            work_type="insulator_washing",
            severity=Severity.MEDIUM,
            overdue_days=6,
            est_duration_min=90,
            block_type=BlockType.POWER_BLOCK,
            crew=["OHE-TOWER-1"],
            equipment=["JET-WASHER-1"],
            depends_on=[],
            isolation_required=True,
            source_meta=SourceMetadata(source="SMMS", mode=SourceMode.SYNTHETIC, last_sync="14:18", confidence=0.93),
        ),
        MaintenanceTask(
            task_id="ENG-105",
            department=Department.ENGG,
            asset_id="TRK-SEC-58",
            corridor="C-01",
            km_from=158.0,
            km_to=159.8,
            work_type="tamping_operation",
            severity=Severity.LOW,
            overdue_days=2,
            est_duration_min=120,
            block_type=BlockType.TRAFFIC_BLOCK,
            crew=["ENGG-CREW-3"],
            equipment=["TAMPING-MACHINE-9"],
            depends_on=[],
            isolation_required=False,
            source_meta=SourceMetadata(source="TMS", mode=SourceMode.SYNTHETIC, last_sync="14:22", confidence=0.95),
        ),
    ]
    return tasks
