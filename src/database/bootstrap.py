"""Idempotent bootstrap data for a fresh database."""

import logging
import time
from typing import Dict

from sqlalchemy.exc import IntegrityError

from . import SessionLocal
from .models import Role

logger = logging.getLogger(__name__)

DEFAULT_ROLES: Dict[str, Dict[str, object]] = {
    "admin": {
        "description": "Full administrative access",
        "permissions": {"admin": True},
    },
    "compliance-officer": {
        "description": "Read and run compliance checks",
        "permissions": {"compliance": True},
    },
    "security-officer": {
        "description": "Read security posture data",
        "permissions": {"security": True},
    },
    "user": {
        "description": "Baseline authenticated access",
        "permissions": {"user": True},
    },
}


def ensure_default_roles() -> int:
    """Create the default RBAC roles when they are missing.

    Returns the number of roles created.
    """
    for attempt in range(5):
        created = 0
        db = SessionLocal()
        try:
            for name, values in DEFAULT_ROLES.items():
                if db.query(Role).filter(Role.name == name).first() is None:
                    db.add(
                        Role(
                            name=name,
                            description=str(values["description"]),
                            permissions=values["permissions"],
                        )
                    )
                    created += 1
            if created:
                db.commit()
                logger.info("Created %s default RBAC roles", created)
            return created
        except IntegrityError:
            db.rollback()
            logger.info("Role seeding raced another worker; retrying")
            time.sleep(0.2 * (attempt + 1))
        except Exception:
            db.rollback()
            logger.exception("Could not seed default RBAC roles")
            return 0
        finally:
            db.close()
    return 0
