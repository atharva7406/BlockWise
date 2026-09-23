from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, CheckConstraint
from .database import Base


class TaskRecord(Base):
    """
    Relational canonical task table storing normalized attributes alongside
    the full raw canonical payload in a JSON/JSONB column for exact audit replay.
    Includes a database constraint blocking 'synthetic' mode records from being
    marked schedulable in production (Blueprint §4).
    """
    __tablename__ = "canonical_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False)
    department = Column(String(32), index=True, nullable=False)
    asset_id = Column(String(64), index=True, nullable=False)
    corridor = Column(String(32), default="C-01", index=True)
    km_from = Column(Float, nullable=False)
    km_to = Column(Float, nullable=False)
    work_type = Column(String(64), nullable=False)
    severity = Column(String(32), default="medium")
    health_state = Column(String(32), default="VALID", index=True)
    priority_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.85)
    mode = Column(String(32), default="synthetic", nullable=False)
    is_scheduled = Column(Boolean, default=False)
    is_production = Column(Boolean, default=False)
    raw_payload = Column(JSON, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "NOT (is_production = 1 AND mode = 'synthetic')",
            name="ck_prevent_synthetic_in_prod",
        ),
    )


class BundleCertificateRecord(Base):
    """
    Immutable Auto-Shadow bundle certificate table for verification and audit.
    """
    __tablename__ = "bundle_certificates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    certificate_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(String(64), nullable=False)
    task_a_id = Column(String(64), nullable=False)
    task_b_id = Column(String(64), nullable=False)
    corridor = Column(String(32), default="C-01")
    km_overlap_range = Column(String(64), nullable=False)
    time_saved_min = Column(Integer, default=0)
    authorized_by = Column(String(64), default="AUTO_SHADOW_ENGINE_G8")
    raw_payload = Column(JSON, nullable=False)


class PlanAuditRecord(Base):
    """
    Statutory officer action audit table with mandatory justification reasons.
    """
    __tablename__ = "plan_audit_rows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(String(64), nullable=False)
    task_id = Column(String(64), index=True, nullable=False)
    action = Column(String(32), nullable=False)  # APPROVE or OVERRIDE
    officer_id = Column(String(64), nullable=False)
    mandatory_reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    raw_payload = Column(JSON, nullable=False)
