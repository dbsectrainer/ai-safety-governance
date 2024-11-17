"""
Models router for handling AI model management endpoints.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from ..schemas import (
    VersionCreate,
    VersionUpdate,
    VersionInDB,
    MonitoringLogCreate,
    MonitoringLogInDB
)
from ..security import get_current_active_user
from ...database import get_db
from ...database.models import User, ModelVersion, MonitoringLog

router = APIRouter()

@router.post("/versions", response_model=VersionInDB)
async def create_model_version(
    model_version: VersionCreate,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new model version.
    """
    db_model_version = ModelVersion(**model_version.dict())
    
    try:
        db.add(db_model_version)
        db.commit()
        db.refresh(db_model_version)
        return db_model_version
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating model version: {str(e)}"
        )

@router.get("/versions", response_model=List[VersionInDB])
async def list_model_versions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all model versions.
    """
    model_versions = db.query(ModelVersion).offset(skip).limit(limit).all()
    return model_versions

@router.get("/versions/{version_id}", response_model=VersionInDB)
async def get_model_version(
    version_id: int,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get specific model version by ID.
    """
    model_version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    return model_version

@router.put("/versions/{version_id}", response_model=VersionInDB)
async def update_model_version(
    version_id: int,
    model_update: VersionUpdate,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update model version details.
    """
    model_version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    
    # Update model version attributes
    for field, value in model_update.dict(exclude_unset=True).items():
        setattr(model_version, field, value)
    
    try:
        db.commit()
        db.refresh(model_version)
        return model_version
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating model version: {str(e)}"
        )

@router.post("/monitoring", response_model=MonitoringLogInDB)
async def create_monitoring_log(
    log_entry: MonitoringLogCreate,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new monitoring log entry.
    """
    # Verify model version exists
    model_version = db.query(ModelVersion).filter(
        ModelVersion.id == log_entry.version_id
    ).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    
    db_log = MonitoringLog(**log_entry.dict())
    
    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating monitoring log: {str(e)}"
        )

@router.get("/monitoring/{model_version_id}", response_model=List[MonitoringLogInDB])
async def get_model_monitoring_logs(
    model_version_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_active_user, scopes=["models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get monitoring logs for a specific model version.
    """
    logs = db.query(MonitoringLog).filter(
        MonitoringLog.version_id == model_version_id
    ).offset(skip).limit(limit).all()
    
    return logs

@router.delete("/versions/{version_id}")
async def delete_model_version(
    version_id: int,
    current_user: User = Security(get_current_active_user, scopes=["admin", "models"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a model version. Requires admin or models scope.
    """
    model_version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found"
        )
    
    try:
        # Delete associated monitoring logs first
        db.query(MonitoringLog).filter(
            MonitoringLog.version_id == version_id
        ).delete()
        
        # Delete model version
        db.delete(model_version)
        db.commit()
        return {"message": f"Model version {version_id} successfully deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting model version: {str(e)}"
        )
