"""
Compliance router for handling compliance-related endpoints.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from ..schemas import (
    ComplianceRecordCreate,
    ComplianceRecordUpdate,
    ComplianceRecordInDB,
    AuditLogCreate,
    AuditLogInDB
)
from ..security import get_current_active_user
from ...database import get_db
from ...database.models import User, ComplianceRecord, AuditLog

router = APIRouter()

@router.post("/records", response_model=ComplianceRecordInDB)
async def create_compliance_record(
    record: ComplianceRecordCreate,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new compliance record.
    """
    db_record = ComplianceRecord(**record.dict())
    
    try:
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # Create audit log for the action
        audit_log = AuditLog(
            user_id=current_user.id,
            action="create",
            resource_type="compliance_record",
            resource_id=str(db_record.id),
            details={"regulation_type": record.regulation_type}
        )
        db.add(audit_log)
        db.commit()
        
        return db_record
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating compliance record: {str(e)}"
        )

@router.get("/records", response_model=List[ComplianceRecordInDB])
async def list_compliance_records(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all compliance records.
    """
    records = db.query(ComplianceRecord).offset(skip).limit(limit).all()
    return records

@router.get("/records/{record_id}", response_model=ComplianceRecordInDB)
async def get_compliance_record(
    record_id: int,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get specific compliance record by ID.
    """
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )
    return record

@router.put("/records/{record_id}", response_model=ComplianceRecordInDB)
async def update_compliance_record(
    record_id: int,
    record_update: ComplianceRecordUpdate,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update compliance record details.
    """
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )
    
    # Update record attributes
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    try:
        db.commit()
        db.refresh(record)
        
        # Create audit log for the update
        audit_log = AuditLog(
            user_id=current_user.id,
            action="update",
            resource_type="compliance_record",
            resource_id=str(record_id),
            details=record_update.dict(exclude_unset=True)
        )
        db.add(audit_log)
        db.commit()
        
        return record
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating compliance record: {str(e)}"
        )

@router.get("/audit-logs", response_model=List[AuditLogInDB])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all audit logs.
    """
    logs = db.query(AuditLog).offset(skip).limit(limit).all()
    return logs

@router.get("/audit-logs/{resource_type}/{resource_id}", response_model=List[AuditLogInDB])
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    current_user: User = Security(get_current_active_user, scopes=["compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get audit logs for a specific resource.
    """
    logs = db.query(AuditLog).filter(
        AuditLog.resource_type == resource_type,
        AuditLog.resource_id == resource_id
    ).all()
    return logs

@router.delete("/records/{record_id}")
async def delete_compliance_record(
    record_id: int,
    current_user: User = Security(get_current_active_user, scopes=["admin", "compliance"]),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a compliance record. Requires admin or compliance scope.
    """
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )
    
    try:
        # Create audit log for the deletion
        audit_log = AuditLog(
            user_id=current_user.id,
            action="delete",
            resource_type="compliance_record",
            resource_id=str(record_id),
            details={"regulation_type": record.regulation_type}
        )
        db.add(audit_log)
        
        # Delete the record
        db.delete(record)
        db.commit()
        return {"message": f"Compliance record {record_id} successfully deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting compliance record: {str(e)}"
        )
