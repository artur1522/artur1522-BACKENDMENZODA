"""Helpers de columnas con paridad exacta al DDL generado por Prisma."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import MappedColumn, mapped_column

TIMESTAMPTZ = TIMESTAMP(timezone=True, precision=6)


def uuid_pk() -> MappedColumn[uuid.UUID]:
    """UUID PK generado por la aplicación (Prisma @default(uuid()))."""
    return mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)


def timestamptz_col() -> MappedColumn[datetime]:
    """TIMESTAMPTZ(6) sin default: el valor lo aporta la aplicación."""
    return mapped_column(TIMESTAMPTZ)


def created_at_col() -> MappedColumn[datetime]:
    """TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP (Prisma @default(now()))."""
    return mapped_column(
        TIMESTAMPTZ,
        default=lambda: datetime.now(UTC),
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )


def updated_at_col() -> MappedColumn[datetime]:
    """TIMESTAMPTZ(6) NOT NULL sin default: la actualiza el ORM (Prisma @updatedAt)."""
    return mapped_column(TIMESTAMPTZ, onupdate=sa.text("CURRENT_TIMESTAMP"))
