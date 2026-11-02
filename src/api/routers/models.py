"""
Models router for handling AI model management endpoints.
"""

import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from ..schemas import (
    MonitoringLogCreate,
    MonitoringLogInDB,
    VersionCreate,
    VersionInDB,
    VersionUpdate,
)
from ..security import get_current_active_user
from ...database import get_db
from ...database.models import AuditLog, ModelVersion, MonitoringLog, User

logger = logging.getLogger(__name__)

router = APIRouter()


def _add_audit(
    db: Session,
    user: User,
    action: str,
    resource_type: str,
    resource_id: Any,
    details: dict,
) -> None:
    db.add(
        AuditLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=jsonable_encoder(details),
        )
    )


@router.post("/versions", response_model=VersionInDB, status_code=status.HTTP_201_CREATED)
async def create_model_version(
    model_version: VersionCreate,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """Register a model version."""
    existing = (
        db.query(ModelVersion)
        .filter(
            ModelVersion.name == model_version.name,
            ModelVersion.version == model_version.version,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This model version is already registered",
        )

    db_model_version = ModelVersion(**model_version.model_dump())

    try:
        db.add(db_model_version)
        db.flush()
        _add_audit(
            db,
            current_user,
            "create",
            "model_version",
            db_model_version.id,
            {"name": db_model_version.name, "version": db_model_version.version},
        )
        db.commit()
        db.refresh(db_model_version)
        return db_model_version
    except Exception:
        db.rollback()
        logger.exception("Failed to create model version")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the model version. Please try again later.",
        )


@router.get("/versions", response_model=List[VersionInDB])
async def list_model_versions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """List registered model versions."""
    return (
        db.query(ModelVersion)
        .order_by(ModelVersion.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/versions/{version_id}", response_model=VersionInDB)
async def get_model_version(
    version_id: int,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """Get a model version by ID."""
    model_version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    return model_version


@router.put("/versions/{version_id}", response_model=VersionInDB)
async def update_model_version(
    version_id: int,
    model_update: VersionUpdate,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """Update model version metadata or deployment state."""
    model_version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )

    updates = model_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(model_version, field, value)

    try:
        _add_audit(db, current_user, "update", "model_version", version_id, updates)
        db.commit()
        db.refresh(model_version)
        return model_version
    except Exception:
        db.rollback()
        logger.exception("Failed to update model version %s", version_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update the model version. Please try again later.",
        )


@router.post("/monitoring", response_model=MonitoringLogInDB, status_code=status.HTTP_201_CREATED)
async def create_monitoring_log(
    log_entry: MonitoringLogCreate,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """Record a monitoring metric for a model version."""
    model_version = db.query(ModelVersion).filter(ModelVersion.id == log_entry.version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )

    db_log = MonitoringLog(**log_entry.model_dump())

    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception:
        db.rollback()
        logger.exception("Failed to create monitoring log")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the monitoring log. Please try again later.",
        )


@router.get("/monitoring/{model_version_id}", response_model=List[MonitoringLogInDB])
async def get_model_monitoring_logs(
    model_version_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """Get monitoring logs for a specific model version."""
    return (
        db.query(MonitoringLog)
        .filter(MonitoringLog.version_id == model_version_id)
        .order_by(MonitoringLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.delete("/versions/{version_id}")
async def delete_model_version(
    version_id: int,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a model version and its monitoring logs."""
    model_version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )

    try:
        _add_audit(
            db,
            current_user,
            "delete",
            "model_version",
            version_id,
            {"name": model_version.name, "version": model_version.version},
        )
        db.delete(model_version)
        db.commit()
        return {"message": f"Model version {version_id} successfully deleted"}
    except Exception:
        db.rollback()
        logger.exception("Failed to delete model version %s", version_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the model version. Please try again later.",
        )
