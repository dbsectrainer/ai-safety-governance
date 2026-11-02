"""
Security utilities for authentication and authorization.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .schemas import TokenData
from ..database import get_db
from ..database.models import User

logger = logging.getLogger(__name__)

# Security configuration. The default is deliberately obvious and is reported by
# the security posture endpoint so deployments do not silently ship it.
DEFAULT_SECRET_KEY = "your-secret-key-for-development-only"
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Scopes used by the API. A superuser receives all of them; role permissions may
# grant individual scopes to regular users.
ALL_SCOPES = ("user", "admin", "models", "compliance", "security")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/token",
    scopes={
        "user": "Read user information",
        "admin": "Full administrative access",
        "models": "Access to model management",
        "compliance": "Access to compliance data",
        "security": "Access to security posture data",
    },
)


def is_default_secret_key() -> bool:
    """Whether the application is using the insecure development secret."""
    return SECRET_KEY == DEFAULT_SECRET_KEY


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:  # pragma: no cover - defensive against malformed hashes
        logger.exception("Password verification failed")
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def scopes_for_user(user: User) -> List[str]:
    """Return the OAuth2 scopes granted to a user.

    Superusers receive every scope so the administrative UI can exercise the
    model, compliance and security APIs. Regular users receive their role
    permission scopes, plus the baseline ``user`` scope.
    """
    scopes = {"user"}
    if user.is_superuser:
        scopes.update(ALL_SCOPES)
    scopes.update(user.permission_scopes)
    return sorted(scopes)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a bearer token and enforce scopes."""
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes") or []
        if not isinstance(token_scopes, list):
            token_scopes = []
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    granted = set(token_data.scopes)
    for scope in security_scopes.scopes:
        if scope not in granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["user"]),
) -> User:
    """Get the current user and reject deactivated accounts."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def verify_admin(user: User) -> bool:
    """Verify if user has admin privileges."""
    return bool(user.is_superuser)


class RoleChecker:
    """Role-based access control checker for role names."""

    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles

    def __call__(self, user: User = Security(get_current_active_user)) -> User:
        role_names = set(user.role_names)
        if user.is_superuser:
            role_names.add("admin")
        if not role_names.intersection(self.required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return user
