"""Auditoría inmutable de acciones de usuario (con índices DESC como en Prisma)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import created_at_col, uuid_pk
from app.models.enums import AuditAction, AuditResult

if TYPE_CHECKING:
    from app.models.identity import Role, User


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        sa.Index("audit_events_occurred_at_idx", sa.text("occurred_at DESC")),
        sa.Index(
            "audit_events_user_id_occurred_at_idx",
            "user_id",
            sa.text("occurred_at DESC"),
        ),
        sa.Index(
            "audit_events_module_key_occurred_at_idx",
            "module_key",
            sa.text("occurred_at DESC"),
        ),
        sa.Index("audit_events_entity_type_entity_id_idx", "entity_type", "entity_id"),
        sa.Index("audit_events_request_id_idx", "request_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    occurred_at: Mapped[datetime] = created_at_col()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("roles.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    user_name_snapshot: Mapped[str] = mapped_column(sa.String(160))
    role_name_snapshot: Mapped[str | None] = mapped_column(sa.String(80))
    action: Mapped[AuditAction] = mapped_column(sa.Enum(AuditAction, name="audit_action"))
    module_key: Mapped[str] = mapped_column(sa.String(80))
    entity_type: Mapped[str | None] = mapped_column(sa.String(80))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(sa.Uuid)
    reference_snapshot: Mapped[str | None] = mapped_column(sa.String(120))
    description: Mapped[str] = mapped_column(sa.Text)
    result: Mapped[AuditResult] = mapped_column(sa.Enum(AuditResult, name="audit_result"))
    changes: Mapped[list] = mapped_column(JSONB, default=list, server_default=sa.text("'[]'"))
    detail: Mapped[str | None] = mapped_column(sa.Text)
    ip: Mapped[str | None] = mapped_column(INET)
    device: Mapped[str | None] = mapped_column(sa.Text)
    request_id: Mapped[uuid.UUID | None] = mapped_column(sa.Uuid)

    user: Mapped[User | None] = relationship(back_populates="audit_events")
    role: Mapped[Role | None] = relationship(back_populates="audit_events")
