"""
Users router for handling user management endpoints.
"""

import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from ..schemas import UserCreate, UserInDB, UserUpdate
from ..security import get_current_active_user, get_password_hash
from ..serializers import serialize_user
from ...database import get_db
from ...database.models import AuditLog, User

logger = logging.getLogger(__name__)

router = APIRouter()

# Admin-only dependency reused by every administrative endpoint.
require_admin = [Security(get_current_active_user, scopes=["admin"])]


@router.get("/me", response_model=UserInDB)
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user information including roles."""
    return serialize_user(current_user)


@router.put("/me", response_model=UserInDB)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update the authenticated user's profile."""
    if user_update.username and user_update.username != current_user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    if user_update.email and user_update.email != current_user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    updates = user_update.model_dump(exclude_unset=True)
    # Profile self-service cannot escalate privileges or deactivate itself.
    updates.pop("is_superuser", None)
    updates.pop("is_active", None)
    password = updates.pop("password", None)
    if password:
        updates["hashed_password"] = get_password_hash(password)

    for field, value in updates.items():
        setattr(current_user, field, value)

    try:
        db.commit()
        db.refresh(current_user)
        return serialize_user(current_user)
    except Exception:
        db.rollback()
        logger.exception("Failed to update current user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update the account. Please try again later.",
        )


@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """Create a user (admin only). Allows creating additional administrators."""
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
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
    )

    try:
        db.add(db_user)
        db.flush()
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="create",
                resource_type="user",
                resource_id=str(db_user.id),
                details={
                    "username": db_user.username,
                    "is_superuser": db_user.is_superuser,
                },
            )
        )
        db.commit()
        db.refresh(db_user)
        return serialize_user(db_user)
    except Exception:
        db.rollback()
        logger.exception("Failed to create user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the user. Please try again later.",
        )


@router.get("/", response_model=List[UserInDB])
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """List all users. Requires admin scope."""
    users = db.query(User).order_by(User.id).offset(skip).limit(limit).all()
    return [serialize_user(user) for user in users]


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(
    user_id: int,
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """Get a user by ID. Requires admin scope."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return serialize_user(user)


@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """Update a user by ID. Requires admin scope."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_update.username and user_update.username != user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    if user_update.email and user_update.email != user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user.id == current_user.id:
        if user_update.is_superuser is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove your own administrator privileges",
            )
        if user_update.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account",
            )

    updates = user_update.model_dump(exclude_unset=True)
    password = updates.pop("password", None)
    if password:
        updates["hashed_password"] = get_password_hash(password)

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="update",
                resource_type="user",
                resource_id=str(user.id),
                details={"fields": sorted(updates.keys())},
            )
        )
        db.commit()
        db.refresh(user)
        return serialize_user(user)
    except Exception:
        db.rollback()
        logger.exception("Failed to update user %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update the user. Please try again later.",
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a user by ID. Requires admin scope."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    try:
        # Audit rows are historical records; keep them but detach the user.
        db.query(AuditLog).filter(AuditLog.user_id == user.id).update(
            {AuditLog.user_id: None}, synchronize_session=False
        )
        db.delete(user)
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="delete",
                resource_type="user",
                resource_id=str(user_id),
                details={"username": user.username},
            )
        )
        db.commit()
        return {"message": f"User {user_id} successfully deleted"}
    except Exception:
        db.rollback()
        logger.exception("Failed to delete user %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the user. Please try again later.",
        )
