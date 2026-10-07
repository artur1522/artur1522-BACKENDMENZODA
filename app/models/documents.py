"""Documentos, programación de reportes y secuencias de numeración."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import created_at_col, timestamptz_col, updated_at_col, uuid_pk
from app.models.enums import DocumentCategory, ReportFrequency

if TYPE_CHECKING:
    from app.models.catalog import Customer, Supplier
    from app.models.identity import User
    from app.models.sales import BusinessOrder


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        sa.Index("documents_storage_key_key", "storage_key", unique=True),
        sa.Index("documents_category_created_at_idx", "category", "created_at"),
        sa.Index("documents_related_order_id_idx", "related_order_id"),
        sa.Index("documents_related_customer_id_idx", "related_customer_id"),
        sa.Index("documents_related_supplier_id_idx", "related_supplier_id"),
        sa.Index("documents_uploaded_by_user_id_idx", "uploaded_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(sa.String(255))
    category: Mapped[DocumentCategory] = mapped_column(
        sa.Enum(DocumentCategory, name="document_category")
    )
    storage_key: Mapped[str | None] = mapped_column(sa.Text)
    mime_type: Mapped[str | None] = mapped_column(sa.String(120))
    byte_size: Mapped[int | None] = mapped_column(sa.BigInteger)
    version_label: Mapped[str] = mapped_column(sa.String(40))
    related_order_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    related_customer_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    related_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()
    deleted_at: Mapped[datetime | None] = timestamptz_col()

    related_order: Mapped[BusinessOrder | None] = relationship(back_populates="documents")
    related_customer: Mapped[Customer | None] = relationship(back_populates="documents")
    related_supplier: Mapped[Supplier | None] = relationship(back_populates="documents")
    uploaded_by: Mapped[User | None] = relationship(back_populates="uploaded_documents")


class ReportSchedule(Base):
    __tablename__ = "report_schedules"
    __table_args__ = (
        sa.Index("report_schedules_report_key_key", "report_key", unique=True),
        sa.Index("report_schedules_is_enabled_frequency_idx", "is_enabled", "frequency"),
        sa.Index("report_schedules_created_by_user_id_idx", "created_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    report_key: Mapped[str] = mapped_column(sa.String(80))
    recipient_email: Mapped[str] = mapped_column(sa.String(254))
    frequency: Mapped[ReportFrequency] = mapped_column(
        sa.Enum(ReportFrequency, name="report_frequency")
    )
    is_enabled: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    created_by: Mapped[User | None] = relationship(back_populates="report_schedules")


class DocumentSequence(Base):
    __tablename__ = "document_sequences"
    __table_args__ = (
        sa.Index(
            "document_sequences_document_type_fiscal_year_idx",
            "document_type",
            "fiscal_year",
        ),
    )

    document_type: Mapped[str] = mapped_column(sa.String(32), primary_key=True)
    fiscal_year: Mapped[int] = mapped_column(sa.SmallInteger, primary_key=True)
    series: Mapped[str] = mapped_column(
        sa.String(12), primary_key=True, default="", server_default=sa.text("''")
    )
    last_value: Mapped[int] = mapped_column(sa.BigInteger, default=0, server_default=sa.text("0"))
    updated_at: Mapped[datetime] = updated_at_col()
