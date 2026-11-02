"""
Authentication router for handling user authentication endpoints.
"""

import logging
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..schemas import Token, UserCreate, UserInDB
from ..security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    scopes_for_user,
    verify_password,
)
from ..serializers import serialize_user
from ...database import get_db
from ...database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


def _find_user(db: Session, identifier: str) -> Optional[User]:
    """Find a user by email or username (login accepts both)."""
    return (
        db.query(User)
        .filter(or_(User.email == identifier, User.username == identifier))
        .first()
    )


def _token_response(user: User) -> dict:
    scopes = scopes_for_user(user)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    """OAuth2 compatible token login using an email address or username."""
    user = _find_user(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _token_response(user)


@router.post("/register", response_model=UserInDB)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Register a new user.

    Self-registration always creates an active, non-superuser account; the
    ``is_superuser`` field in the payload is intentionally ignored.
    """
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_superuser=False,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return serialize_user(db_user)
    except Exception:
        db.rollback()
        logger.exception("Failed to register user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the account. Please try again later.",
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    """Issue a fresh token after re-checking the supplied credentials.

    This endpoint previously accepted any password for a known username, which
    allowed token issuance without authentication. It now verifies the password
    exactly like the login endpoint.
    """
    user = _find_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _token_response(user)


@router.post("/logout")
async def logout():
    """Logout user.

    JWTs cannot be revoked server-side without a token denylist, so the client
    discards the token. This endpoint exists for a symmetric API surface.
    """
    return {"message": "Successfully logged out"}
