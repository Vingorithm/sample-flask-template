"""Example model. Replace or extend it for your project."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import INDEXED_STRING_MAX, TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(INDEXED_STRING_MAX), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
