"""
Compliance router for handling compliance-related endpoints.
"""

import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from ..schemas import (
    AuditLogInDB,
    ComplianceRecordCreate,
    ComplianceRecordInDB,
    ComplianceRecordUpdate,
)
from ..security import get_current_active_user
from ...compliance.checks import build_configuration_rules
from ...compliance.regulatory_alignment import RegulatoryAlignmentSystem
from ...database import PROJECT_ROOT, get_db
from ...utils.time import utcnow
from ...database.models import AuditLog, ComplianceRecord, User

logger = logging.getLogger(__name__)

router = APIRouter()

CONFIG_PATH = Path(
    os.getenv(
        "COMPLIANCE_CONFIG_PATH",
        str(PROJECT_ROOT / "config" / "compliance_config.json"),
    )
)
AUDIT_DIR = Path(os.getenv("COMPLIANCE_AUDIT_DIR", str(PROJECT_ROOT / "compliance_logs")))

STATUS_MAP = {
    "COMPLIANT": "compliant",
    "NON_COMPLIANT": "non_compliant",
    "NEEDS_REVIEW": "needs_review",
    "ERROR": "needs_review",
}


def _audit(db: Session, user: User, action: str, record_id: Any, details: Dict[str, Any]) -> None:
    db.add(
        AuditLog(
            user_id=user.id,
            action=action,
            resource_type="compliance_record",
            resource_id=str(record_id),
            details=jsonable_encoder(details),
        )
    )


def _latest_records(db: Session) -> List[ComplianceRecord]:
    records = db.query(ComplianceRecord).order_by(ComplianceRecord.created_at.desc()).all()
    latest: Dict[str, ComplianceRecord] = {}
    for record in records:
        latest.setdefault(record.regulation_type, record)
    return list(latest.values())


@router.post("/checks/run")
async def run_compliance_checks(
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Run the configured compliance checks and persist a snapshot.

    This executes the configuration-level checks in
    ``src.compliance.checks``, writes an audit report under ``compliance_logs/``
    and stores one record per regulation. It does not certify legal compliance.
    """
    try:
        system = RegulatoryAlignmentSystem(
            config_path=str(CONFIG_PATH),
            audit_trail_dir=str(AUDIT_DIR),
        )
        for rule in build_configuration_rules(system.config):
            system.register_compliance_rule(rule)

        results = system.run_compliance_checks()
        report_path = system.generate_compliance_report(results)
        review_days = int(system.config.get("check_frequency_days", 30))
        next_review = utcnow() + timedelta(days=review_days)

        created = []
        for item in results["rules_status"]:
            record = ComplianceRecord(
                regulation_type=item["regulation"],
                status=STATUS_MAP.get(item["status"], "needs_review"),
                details={
                    "description": item["description"],
                    "rule_id": item["rule_id"],
                    "checked_at": results["timestamp"],
                    "source": "configuration_check",
                    "error": item.get("error"),
                },
                next_review_date=next_review,
            )
            db.add(record)
            created.append(record)

        db.add(
            AuditLog(
                user_id=current_user.id,
                action="run_checks",
                resource_type="compliance_check",
                resource_id=Path(report_path).name,
                details=jsonable_encoder(
                    {
                        "compliant_rules": results["compliant_rules"],
                        "non_compliant_rules": results["non_compliant_rules"],
                        "error_rules": results["error_rules"],
                    }
                ),
            )
        )
        db.commit()
        for record in created:
            db.refresh(record)

        total = len(results["rules_status"])
        score = round((results["compliant_rules"] / total) * 100) if total else 0

        return {
            "summary": {
                "total_rules": total,
                "compliant_rules": results["compliant_rules"],
                "non_compliant_rules": results["non_compliant_rules"],
                "error_rules": results["error_rules"],
                "score": score,
            },
            "report": Path(report_path).name,
            "records": [jsonable_encoder(record) for record in created],
        }
    except Exception:
        db.rollback()
        logger.exception("Compliance check run failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to run compliance checks. Please try again later.",
        )


@router.get("/summary")
async def get_compliance_summary(
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Return the latest compliance snapshot per regulation."""
    latest = _latest_records(db)
    counts = {"compliant": 0, "non_compliant": 0, "needs_review": 0}
    for record in latest:
        counts[record.status] = counts.get(record.status, 0) + 1

    score = 0
    if latest:
        weighted = sum(
            (100 if record.status == "compliant" else 50 if record.status == "needs_review" else 0)
            for record in latest
        )
        score = round(weighted / len(latest))

    last_run = max((record.created_at for record in latest), default=None)

    return {
        "score": score,
        "total_regulations": len(latest),
        "status_counts": counts,
        "last_run": last_run,
        "latest": [
            jsonable_encoder(record) for record in sorted(latest, key=lambda r: r.regulation_type)
        ],
    }


@router.post("/records", response_model=ComplianceRecordInDB, status_code=status.HTTP_201_CREATED)
async def create_compliance_record(
    record: ComplianceRecordCreate,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Create a compliance record manually."""
    db_record = ComplianceRecord(**record.model_dump())

    try:
        db.add(db_record)
        db.flush()
        _audit(
            db,
            current_user,
            "create",
            db_record.id,
            {"regulation_type": record.regulation_type},
        )
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception:
        db.rollback()
        logger.exception("Failed to create compliance record")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the compliance record. Please try again later.",
        )


@router.get("/records", response_model=List[ComplianceRecordInDB])
async def list_compliance_records(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """List compliance records, newest first."""
    return (
        db.query(ComplianceRecord)
        .order_by(ComplianceRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/records/{record_id}", response_model=ComplianceRecordInDB)
async def get_compliance_record(
    record_id: int,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Get a compliance record by ID."""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found",
        )
    return record


@router.put("/records/{record_id}", response_model=ComplianceRecordInDB)
async def update_compliance_record(
    record_id: int,
    record_update: ComplianceRecordUpdate,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Update a compliance record."""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found",
        )

    updates = record_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)

    try:
        _audit(db, current_user, "update", record_id, updates)
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        logger.exception("Failed to update compliance record %s", record_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update the compliance record. Please try again later.",
        )


@router.get("/audit-logs", response_model=List[AuditLogInDB])
async def list_audit_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """List audit logs, newest first."""
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/audit-logs/{resource_type}/{resource_id}", response_model=List[AuditLogInDB])
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Get audit logs for a specific resource."""
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id,
        )
        .order_by(AuditLog.timestamp.desc())
        .all()
    )


@router.delete("/records/{record_id}")
async def delete_compliance_record(
    record_id: int,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a compliance record and keep an audit entry."""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found",
        )

    try:
        _audit(
            db,
            current_user,
            "delete",
            record_id,
            {"regulation_type": record.regulation_type},
        )
        db.delete(record)
        db.commit()
        return {"message": f"Compliance record {record_id} successfully deleted"}
    except Exception:
        db.rollback()
        logger.exception("Failed to delete compliance record %s", record_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the compliance record. Please try again later.",
        )
