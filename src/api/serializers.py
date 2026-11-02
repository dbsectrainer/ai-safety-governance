"""Shared response serializers."""

from typing import Any, Dict

from ..database.models import User


def serialize_user(user: User) -> Dict[str, Any]:
    """Serialize a user without exposing password material."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": user.role_names,
    }
