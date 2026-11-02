"""
Database models for AI Safety Governance Platform.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship("AuditLog", back_populates="user")

    @property
    def role_names(self) -> list[str]:
        """Return role names, including the implicit admin role for superusers."""
        names = [
            user_role.role.name
            for user_role in self.roles
            if user_role.role is not None
        ]
        if self.is_superuser and "admin" not in names:
            names.insert(0, "admin")
        return names

    @property
    def permission_scopes(self) -> set[str]:
        """Return the scopes granted by assigned roles."""
        scopes: set[str] = set()
        for user_role in self.roles:
            if user_role.role is None or not user_role.role.permissions:
                continue
            scopes.update(user_role.role.permissions.keys())
        return scopes


class Role(Base):
    """Role model for RBAC."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    """Association table for User-Role many-to-many relationship."""

    __tablename__ = "user_roles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class AuditLog(Base):
    """Audit log for tracking system activities."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class ModelVersion(Base):
    """Model version tracking."""

    __tablename__ = "model_versions"
    __table_args__ = (Index("uq_model_version", "name", "version", unique=True),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    version_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deployed_at = Column(DateTime)
    status = Column(String)

    # Relationships
    monitoring_logs = relationship(
        "MonitoringLog", back_populates="model_version", cascade="all, delete-orphan"
    )


class MonitoringLog(Base):
    """Model monitoring logs."""

    __tablename__ = "monitoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(
        Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False
    )
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    model_version = relationship("ModelVersion", back_populates="monitoring_logs")


class ComplianceRecord(Base):
    """Compliance tracking records."""

    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True)
    regulation_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    next_review_date = Column(DateTime)


class SystemMetricSample(Base):
    """Time-series samples for host resource monitoring.

    These are intentionally separate from model monitoring logs because they are
    not tied to a model version.
    """

    __tablename__ = "system_metric_samples"

    id = Column(Integer, primary_key=True, index=True)
    resource = Column(String, nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SystemSetting(Base):
    """Persisted, non-secret platform configuration sections."""

    __tablename__ = "system_settings"

    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
