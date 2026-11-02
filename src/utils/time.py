"""Timezone-safe helpers for naive UTC database timestamps."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current UTC time as a naive datetime.

    The database columns are timezone-naive; using this helper avoids the
    deprecated ``datetime.utcnow`` while preserving the existing storage format.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
