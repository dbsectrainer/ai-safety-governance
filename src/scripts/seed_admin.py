"""Create or update the bootstrap administrator account.

Usage:
    ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='Str0ng!Pass' \
        python -m src.scripts.seed_admin

The same environment variables are also consumed at application startup
(``ensure_admin_from_env``) so Docker deployments can bootstrap safely.
"""

import argparse
import getpass
import logging
import os
import sys
from typing import Optional

from sqlalchemy import or_

from ..api.schemas import PASSWORD_PATTERN
from ..api.security import get_password_hash
from ..database import SessionLocal, init_db
from ..database.models import User

logger = logging.getLogger(__name__)


def seed_admin(
    email: str,
    password: str,
    username: Optional[str] = None,
    full_name: Optional[str] = "Platform Administrator",
    update_password: bool = False,
) -> Optional[User]:
    """Create an administrator, or return the existing account."""
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(
            "ADMIN_PASSWORD must be at least 8 characters and include uppercase, "
            "lowercase, number and special character"
        )

    username = username or email.split("@")[0][:16]
    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(or_(User.email == email, User.username == username))
            .first()
        )
        if user:
            if update_password:
                user.hashed_password = get_password_hash(password)
                db.commit()
                logger.info("Updated password for administrator %s", user.email)
            else:
                logger.info(
                    "Administrator %s already exists; leaving it unchanged", user.email
                )
            return user

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created administrator %s", user.email)
        return user
    finally:
        db.close()


def ensure_admin_from_env() -> Optional[User]:
    """Bootstrap an administrator when both env variables are present."""
    email = os.getenv("ADMIN_EMAIL", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "")
    if not email or not password:
        return None
    try:
        return seed_admin(
            email=email,
            password=password,
            username=os.getenv("ADMIN_USERNAME") or None,
            full_name=os.getenv("ADMIN_FULL_NAME", "Platform Administrator"),
        )
    except Exception:
        logger.exception("Could not bootstrap the administrator account")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an AI Safety Governance administrator"
    )
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"))
    parser.add_argument("--username", default=os.getenv("ADMIN_USERNAME"))
    parser.add_argument(
        "--full-name", default=os.getenv("ADMIN_FULL_NAME", "Platform Administrator")
    )
    parser.add_argument("--update-password", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not args.email:
        parser.error("--email or ADMIN_EMAIL is required")
    password = args.password
    if not password:
        password = getpass.getpass("Admin password: ")

    init_db()
    try:
        user = seed_admin(
            email=args.email,
            password=password,
            username=args.username,
            full_name=args.full_name,
            update_password=args.update_password,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Administrator ready: {user.email} (id={user.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
