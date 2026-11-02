"""Dashboard summary API backed by real database aggregates."""

from datetime import timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from ..security import get_current_active_user
from ...database import get_db
from ...utils.time import utcnow
from ...database.models import AuditLog, ComplianceRecord, ModelVersion, User
from .monitoring import _read_system_metrics

router = APIRouter()


def _compliance_snapshot(db: Session) -> Dict[str, Any]:
    records = db.query(ComplianceRecord).order_by(ComplianceRecord.created_at.desc()).all()
    latest: Dict[str, ComplianceRecord] = {}
    for record in records:
        latest.setdefault(record.regulation_type, record)

    if not latest:
        return {"score": 0, "total": 0, "status_counts": {}}

    counts: Dict[str, int] = {}
    weighted = 0
    for record in latest.values():
        counts[record.status] = counts.get(record.status, 0) + 1
        weighted += (
            100 if record.status == "compliant" else 50 if record.status == "needs_review" else 0
        )
    return {
        "score": round(weighted / len(latest)),
        "total": len(latest),
        "status_counts": counts,
    }


def _performance_series(db: Session) -> List[Dict[str, Any]]:
    """Cumulative user/model counts in 2-hour buckets over the last day."""
    now = utcnow()
    series = []
    for index in range(12, -1, -1):
        bucket = now - timedelta(hours=index * 2)
        series.append(
            {
                "timestamp": int(bucket.timestamp() * 1000),
                "users": db.query(User).filter(User.created_at <= bucket).count(),
                "models": db.query(ModelVersion).filter(ModelVersion.created_at <= bucket).count(),
            }
        )
    return series


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Security(get_current_active_user, scopes=["user"]),
    db: Session = Depends(get_db),
) -> Any:
    """Aggregate counts, health, compliance score, activity and history."""
    resources = _read_system_metrics()
    compliance = _compliance_snapshot(db)
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    active_models = (
        db.query(ModelVersion)
        .filter((ModelVersion.status.is_(None)) | (ModelVersion.status != "retired"))
        .count()
    )

    peak = max(resources["cpu"], resources["memory"], resources["storage"])
    if peak < 70:
        system_health = "Excellent"
    elif peak < 85:
        system_health = "Good"
    elif peak < 95:
        system_health = "Warning"
    else:
        system_health = "Critical"

    can_view_all = current_user.is_superuser or bool(
        {"admin", "compliance"}.intersection(current_user.role_names)
    )
    activity_query = db.query(AuditLog)
    if not can_view_all:
        activity_query = activity_query.filter(AuditLog.user_id == current_user.id)
    activity = activity_query.order_by(AuditLog.timestamp.desc()).limit(8).all()

    return {
        "metrics": {
            "active_users": active_users,
            "active_models": active_models,
            "compliance_score": compliance["score"],
            "system_health": system_health,
        },
        "resources": resources,
        "compliance": compliance,
        "activity": [
            {
                "id": str(log.id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "timestamp": log.timestamp,
            }
            for log in activity
        ],
        "performance": _performance_series(db),
    }
