"""Shared model helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def utcnow() -> datetime:
    """Naive UTC timestamp; MySQL 5.6 DATETIME has no timezone support."""
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )


# MySQL 5.6 + utf8mb4 note:
# InnoDB index keys are limited to 767 bytes on 5.6 (4 bytes per utf8mb4
# char), so any indexed/unique VARCHAR must be String(191) or shorter.
# Also avoid the JSON column type: MySQL 5.6 does not support it.
INDEXED_STRING_MAX = 191
