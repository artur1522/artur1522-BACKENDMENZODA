"""Tesorería: cuentas bancarias y movimientos de caja/banco."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import created_at_col, timestamptz_col, updated_at_col, uuid_pk
from app.models.enums import (
    PaymentMethod,
    ReconciliationStatus,
    TreasuryChannel,
    TreasuryMovementType,
)

if TYPE_CHECKING:
    from app.models.identity import User
    from app.models.purchases import SupplierInvoice
    from app.models.sales import SalesInvoice


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    __table_args__ = (
        sa.Index("bank_accounts_label_key", "label", unique=True),
        sa.Index("bank_accounts_is_active_idx", "is_active"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    label: Mapped[str] = mapped_column(sa.String(120))
    bank_name: Mapped[str | None] = mapped_column(sa.String(80))
    account_reference: Mapped[str | None] = mapped_column(sa.String(80))
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), default="PEN", server_default=sa.text("'PEN'")
    )
    opening_balance: Mapped[Decimal] = mapped_column(
        sa.Numeric(14, 2), default=Decimal("0"), server_default=sa.text("0")
    )
    opening_as_of: Mapped[date | None] = mapped_column(sa.Date)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    treasury_movements: Mapped[list[TreasuryMovement]] = relationship(back_populates="bank_account")


class TreasuryMovement(Base):
    __tablename__ = "treasury_movements"
    __table_args__ = (
        sa.Index("treasury_movements_code_key", "code", unique=True),
        sa.Index("treasury_movements_occurred_at_channel_idx", "occurred_at", "channel"),
        sa.Index(
            "treasury_movements_bank_account_id_occurred_at_idx",
            "bank_account_id",
            "occurred_at",
        ),
        sa.Index(
            "treasury_movements_sales_invoice_id_occurred_at_idx",
            "sales_invoice_id",
            "occurred_at",
        ),
        sa.Index(
            "treasury_movements_supplier_invoice_id_occurred_at_idx",
            "supplier_invoice_id",
            "occurred_at",
        ),
        sa.Index("treasury_movements_created_by_user_id_idx", "created_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(32))
    occurred_at: Mapped[datetime] = timestamptz_col()
    channel: Mapped[TreasuryChannel] = mapped_column(
        sa.Enum(TreasuryChannel, name="treasury_channel")
    )
    movement_type: Mapped[TreasuryMovementType] = mapped_column(
        sa.Enum(TreasuryMovementType, name="treasury_movement_type")
    )
    signed_amount: Mapped[Decimal] = mapped_column(sa.Numeric(14, 2))
    description: Mapped[str] = mapped_column(sa.Text)
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        sa.Enum(PaymentMethod, name="payment_method")
    )
    operation_reference: Mapped[str | None] = mapped_column(sa.String(80))
    bank_account_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("bank_accounts.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    sales_invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("sales_invoices.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    supplier_invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("supplier_invoices.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    reconciliation_status: Mapped[ReconciliationStatus | None] = mapped_column(
        sa.Enum(ReconciliationStatus, name="reconciliation_status")
    )
    note: Mapped[str | None] = mapped_column(sa.Text)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()

    bank_account: Mapped[BankAccount | None] = relationship(back_populates="treasury_movements")
    sales_invoice: Mapped[SalesInvoice | None] = relationship(back_populates="treasury_movements")
    supplier_invoice: Mapped[SupplierInvoice | None] = relationship(
        back_populates="treasury_movements"
    )
    created_by: Mapped[User | None] = relationship(back_populates="created_treasury_movements")
