"""Security posture API backed by configuration and audit data."""

import os
from datetime import timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from ..security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    is_default_secret_key,
)
from ...database import get_db
from ...utils.time import utcnow
from ...database.models import AuditLog, Role, User

router = APIRouter()

EVENT_MESSAGES = {
    ("run_checks", "compliance_check"): "Ran compliance checks",
    ("create", "compliance_record"): "Created compliance record",
    ("update", "compliance_record"): "Updated compliance record",
    ("delete", "compliance_record"): "Deleted compliance record",
    ("create", "model_version"): "Registered model version",
    ("update", "model_version"): "Updated model version",
    ("delete", "model_version"): "Deleted model version",
    ("create", "user"): "Created user",
    ("update", "user"): "Updated user",
    ("delete", "user"): "Deleted user",
    ("update", "settings"): "Updated platform settings",
}


def _event_message(action: str, resource_type: str) -> str:
    known = EVENT_MESSAGES.get((action, resource_type))
    if known:
        return known
    return f"{action.replace('_', ' ').title()} {resource_type.replace('_', ' ')}"


def _cors_is_restricted() -> bool:
    origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    return bool(origins) and "*" not in origins


@router.get("/summary")
async def get_security_summary(
    current_user: User = Security(get_current_active_user, scopes=["security"]),
    db: Session = Depends(get_db),
) -> Any:
    """Report observable security controls and recent audit events."""
    checks: List[Dict[str, Any]] = []

    def add_check(name: str, passed: bool, description: str, severity: str = "medium") -> None:
        checks.append(
            {
                "name": name,
                "passed": passed,
                "description": description,
                "severity": severity,
            }
        )

    roles = db.query(Role).count()
    add_check(
        "rbac_roles",
        roles > 0,
        "At least one RBAC role is configured.",
        "medium",
    )
    add_check(
        "secret_key",
        not is_default_secret_key(),
        "A non-placeholder SECRET_KEY of at least 32 characters is configured.",
        "high",
    )
    add_check(
        "cors",
        _cors_is_restricted(),
        "CORS origins are explicitly restricted (no wildcard).",
        "medium",
    )
    admin_count = (
        db.query(User).filter(User.is_superuser.is_(True), User.is_active.is_(True)).count()
    )
    add_check(
        "admin_account",
        admin_count > 0,
        "At least one active administrator account exists.",
        "high",
    )
    add_check(
        "token_lifetime",
        ACCESS_TOKEN_EXPIRE_MINUTES <= 60,
        "Access tokens expire within 60 minutes.",
        "medium",
    )
    audit_enabled = True
    try:
        db.query(AuditLog).limit(1).all()
    except Exception:  # pragma: no cover - schema/driver failure
        audit_enabled = False
    add_check(
        "audit_logging",
        audit_enabled,
        "The audit log table is available for security events.",
        "high",
    )

    passed = sum(1 for check in checks if check["passed"])
    score = round((passed / len(checks)) * 100) if checks else 0

    cutoff = utcnow() - timedelta(hours=24)
    recent_events = (
        db.query(AuditLog)
        .filter(AuditLog.timestamp >= cutoff)
        .order_by(AuditLog.timestamp.desc())
        .limit(20)
        .all()
    )
    events = [
        {
            "id": str(log.id),
            "type": "warning" if log.action in {"delete", "deactivate"} else "info",
            "message": _event_message(log.action, log.resource_type),
            "timestamp": log.timestamp,
        }
        for log in recent_events
    ]

    recommendations = [
        {
            "id": check["name"],
            "message": check["description"],
            "priority": check["severity"],
            "status": "pending",
        }
        for check in checks
        if not check["passed"]
    ]
    if not recommendations:
        recommendations = [
            {
                "id": "maintain",
                "message": "All observable security checks pass. Continue routine audits.",
                "priority": "low",
                "status": "completed",
            }
        ]

    active_users = db.query(User).filter(User.is_active.is_(True)).count()

    return {
        "score": score,
        "checks": checks,
        "metrics": {
            "security_score": score,
            "active_users": active_users,
            "access_policies": roles,
            "events_24h": len(recent_events),
        },
        "events": events,
        "recommendations": recommendations,
        "generated_at": utcnow(),
    }
