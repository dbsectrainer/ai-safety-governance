"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, constr, ConfigDict

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None

class RoleInDB(RoleBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

# Version Schemas
class VersionBase(BaseModel):
    name: str
    version: str
    version_metadata: Dict[str, Any]  # Changed from metadata to version_metadata
    status: str

class VersionCreate(VersionBase):
    pass

class VersionUpdate(BaseModel):
    version_metadata: Optional[Dict[str, Any]] = None  # Changed from metadata to version_metadata
    status: Optional[str] = None
    deployed_at: Optional[datetime] = None

class VersionInDB(VersionBase):
    id: int
    created_at: datetime
    deployed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# Monitoring Log Schemas
class MonitoringLogBase(BaseModel):
    metric_name: str
    metric_value: Dict[str, Any]

class MonitoringLogCreate(MonitoringLogBase):
    version_id: int

class MonitoringLogInDB(MonitoringLogBase):
    id: int
    version_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Compliance Record Schemas
class ComplianceRecordBase(BaseModel):
    regulation_type: str
    status: str
    details: Dict[str, Any]
    next_review_date: Optional[datetime]

class ComplianceRecordCreate(ComplianceRecordBase):
    pass

class ComplianceRecordUpdate(BaseModel):
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    next_review_date: Optional[datetime] = None

class ComplianceRecordInDB(ComplianceRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Audit Log Schemas
class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]

class AuditLogCreate(AuditLogBase):
    user_id: int

class AuditLogInDB(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Response Schemas
class ResponseBase(BaseModel):
    success: bool
    message: str

class ErrorResponse(ResponseBase):
    success: bool = False
    error_code: str
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(ResponseBase):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
