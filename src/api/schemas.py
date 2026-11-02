"""
Pydantic schemas for API request/response models.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,16}$")
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,128}$"
)


# User Schemas
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: EmailStr
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = True
    is_superuser: bool = False

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not USERNAME_PATTERN.match(value):
            raise ValueError(
                "Username must be 3-16 characters and contain only letters, numbers, "
                "underscores and hyphens"
            )
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be at least 8 characters and include uppercase, "
                "lowercase, number and special character"
            )
        return value


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=16)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not USERNAME_PATTERN.match(value):
            raise ValueError(
                "Username must be 3-16 characters using letters, numbers, _ or -"
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be at least 8 characters and include uppercase, "
                "lowercase, number and special character"
            )
        return value


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    roles: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any] = Field(default_factory=dict)


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
    user: Optional[UserInDB] = None


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)


# Version Schemas
class VersionBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=50)
    version_metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="registered", max_length=50)


class VersionCreate(VersionBase):
    pass


class VersionUpdate(BaseModel):
    version_metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(default=None, max_length=50)
    deployed_at: Optional[datetime] = None


class VersionInDB(VersionBase):
    id: int
    created_at: datetime
    deployed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Monitoring Log Schemas
class MonitoringLogBase(BaseModel):
    metric_name: str = Field(min_length=1, max_length=100)
    metric_value: Dict[str, Any] = Field(default_factory=dict)


class MonitoringLogCreate(MonitoringLogBase):
    version_id: int


class MonitoringLogInDB(MonitoringLogBase):
    id: int
    version_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# Compliance Record Schemas
class ComplianceRecordBase(BaseModel):
    regulation_type: str = Field(min_length=1, max_length=100)
    status: str = Field(min_length=1, max_length=50)
    details: Dict[str, Any] = Field(default_factory=dict)
    next_review_date: Optional[datetime] = None


class ComplianceRecordCreate(ComplianceRecordBase):
    pass


class ComplianceRecordUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=50)
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
    resource_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class AuditLogCreate(AuditLogBase):
    user_id: int


class AuditLogInDB(AuditLogBase):
    id: int
    user_id: Optional[int] = None
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
