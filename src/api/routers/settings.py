"""Persisted, non-secret platform settings."""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from ..security import get_current_active_user
from ...database import get_db
from ...database.models import AuditLog, SystemSetting, User

logger = logging.getLogger(__name__)

router = APIRouter()

DEFAULT_SETTINGS: Dict[str, Dict[str, Any]] = {
    "general": {
        "platform_name": "AI Safety Governance Platform",
        "environment": "development",
        "debug_mode": False,
        "data_retention_days": 30,
        "max_concurrent_models": 10,
    },
    "security": {
        "mfa_enabled": False,
        "session_timeout": 30,
        "password_policy": "strong",
        "ip_whitelist": "",
        "audit_logging": True,
    },
    "notifications": {
        "email_notifications": True,
        "slack_notifications": False,
        "alert_threshold": "medium",
        "daily_digest": True,
        "maintenance_alerts": True,
    },
    "integrations": {
        "aws_region": "us-west-2",
        "monitoring_service": "prometheus",
    },
}

ALLOWED_VALUES = {
    ("general", "environment"): {"development", "staging", "production"},
    ("security", "password_policy"): {"basic", "medium", "strong"},
    ("notifications", "alert_threshold"): {"low", "medium", "high"},
    ("integrations", "monitoring_service"): {"cloudwatch", "datadog", "prometheus"},
}

ALLOWED_RANGES = {
    ("general", "data_retention_days"): (1, 3650),
    ("general", "max_concurrent_models"): (1, 100),
    ("security", "session_timeout"): (1, 1440),
}


def _load(db: Session) -> Dict[str, Any]:
    row = db.query(SystemSetting).filter(SystemSetting.key == "platform").first()
    if row is None:
        row = SystemSetting(key="platform", value=DEFAULT_SETTINGS)
        db.add(row)
        db.commit()
        db.refresh(row)
    merged = {section: dict(values) for section, values in DEFAULT_SETTINGS.items()}
    for section, values in (row.value or {}).items():
        if isinstance(values, dict):
            merged.setdefault(section, {}).update(values)
    return merged


def _validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expected a non-empty object of settings sections",
        )

    cleaned: Dict[str, Any] = {}
    for section, values in payload.items():
        if section not in DEFAULT_SETTINGS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown settings section '{section}'",
            )
        if not isinstance(values, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Settings section '{section}' must be an object",
            )
        cleaned[section] = {}
        for key, value in values.items():
            if key not in DEFAULT_SETTINGS[section]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unknown setting '{section}.{key}'",
                )
            allowed = ALLOWED_VALUES.get((section, key))
            if allowed and value not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid value for '{section}.{key}'",
                )
            value_range = ALLOWED_RANGES.get((section, key))
            if value_range and (
                not isinstance(value, int)
                or isinstance(value, bool)
                or not value_range[0] <= value <= value_range[1]
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"'{section}.{key}' must be an integer between "
                    f"{value_range[0]} and {value_range[1]}",
                )
            if isinstance(value, str) and len(value) > 500:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"'{section}.{key}' is too long",
                )
            cleaned[section][key] = value
    return cleaned


@router.get("")
async def get_settings(
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """Read persisted non-secret platform settings."""
    return {"settings": _load(db), "updated_at": datetime.utcnow()}


@router.put("")
async def update_settings(
    payload: Dict[str, Any],
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """Merge validated settings sections and persist them."""
    updates = _validate(payload)
    row = db.query(SystemSetting).filter(SystemSetting.key == "platform").first()
    if row is None:
        row = SystemSetting(key="platform", value=dict(DEFAULT_SETTINGS))
        db.add(row)
        db.flush()

    merged = {section: dict(values) for section, values in (row.value or {}).items()}
    for section, values in updates.items():
        merged.setdefault(section, {}).update(values)
    row.value = merged
    row.updated_by = current_user.id
    row.updated_at = datetime.utcnow()

    try:
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="update",
                resource_type="settings",
                resource_id="platform",
                details={"sections": sorted(updates.keys())},
            )
        )
        db.commit()
        db.refresh(row)
        return {"settings": merged, "updated_at": row.updated_at}
    except Exception:
        db.rollback()
        logger.exception("Failed to update platform settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save settings. Please try again later.",
        )
