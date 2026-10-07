"""Identidad, seguridad y ajustes globales de la empresa."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import CITEXT, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import created_at_col, timestamptz_col, updated_at_col, uuid_pk
from app.models.enums import CostMethod, RoleType, UserStatus

if TYPE_CHECKING:
    from app.models.audit import AuditEvent
    from app.models.catalog import Customer, Warehouse
    from app.models.documents import Document, ReportSchedule
    from app.models.finance import TreasuryMovement
    from app.models.inventory import InventoryAdjustment, InventoryMovement, InventoryTransfer
    from app.models.purchases import GoodsReceipt, PurchaseRequest, SupplierInvoice
    from app.models.sales import BusinessOrder, Dispatch, OrderStepEvent, Quotation


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        sa.Index("roles_code_key", "code", unique=True),
        sa.Index("roles_name_key", "name", unique=True),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(40))
    name: Mapped[str] = mapped_column(sa.String(80))
    description: Mapped[str | None] = mapped_column(sa.Text)
    role_type: Mapped[RoleType] = mapped_column(
        sa.Enum(RoleType, name="role_type"),
        default=RoleType.CUSTOM,
        server_default=sa.text("'CUSTOM'"),
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    users: Mapped[list[User]] = relationship(back_populates="role")
    permissions: Mapped[list[RolePermission]] = relationship(back_populates="role")
    audit_events: Mapped[list[AuditEvent]] = relationship(back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        sa.Index("permissions_module_key_action_key_key", "module_key", "action_key", unique=True),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    module_key: Mapped[str] = mapped_column(sa.String(80))
    action_key: Mapped[str] = mapped_column(sa.String(16))

    roles: Mapped[list[RolePermission]] = relationship(back_populates="permission")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (sa.Index("role_permissions_permission_id_idx", "permission_id"),)

    role_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("permissions.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    granted: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    updated_at: Mapped[datetime] = updated_at_col()

    role: Mapped[Role] = relationship(back_populates="permissions")
    permission: Mapped[Permission] = relationship(back_populates="roles")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        sa.Index("users_email_key", "email", unique=True),
        sa.Index("users_role_id_status_idx", "role_id", "status"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    role_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("roles.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    full_name: Mapped[str] = mapped_column(sa.String(160))
    email: Mapped[str] = mapped_column(CITEXT)
    password_hash: Mapped[str | None] = mapped_column(sa.Text)
    area: Mapped[str | None] = mapped_column(sa.String(60))
    status: Mapped[UserStatus] = mapped_column(
        sa.Enum(UserStatus, name="user_status"),
        default=UserStatus.INVITED,
        server_default=sa.text("'INVITED'"),
    )
    mfa_enabled: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        sa.SmallInteger, default=0, server_default=sa.text("0")
    )
    locked_until: Mapped[datetime | None] = timestamptz_col()
    last_login_at: Mapped[datetime | None] = timestamptz_col()
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    role: Mapped[Role] = relationship(back_populates="users")
    sessions: Mapped[list[AuthSession]] = relationship(back_populates="user")
    assigned_customers: Mapped[list[Customer]] = relationship(back_populates="salesperson")
    managed_warehouses: Mapped[list[Warehouse]] = relationship(back_populates="manager")
    quotations: Mapped[list[Quotation]] = relationship(back_populates="seller")
    requested_purchase_requests: Mapped[list[PurchaseRequest]] = relationship(
        back_populates="requester",
        foreign_keys="PurchaseRequest.requested_by_user_id",
    )
    reviewed_purchase_requests: Mapped[list[PurchaseRequest]] = relationship(
        back_populates="reviewer",
        foreign_keys="PurchaseRequest.reviewed_by_user_id",
    )
    created_orders: Mapped[list[BusinessOrder]] = relationship(
        back_populates="created_by",
        foreign_keys="BusinessOrder.created_by_user_id",
    )
    sold_orders: Mapped[list[BusinessOrder]] = relationship(
        back_populates="seller",
        foreign_keys="BusinessOrder.seller_user_id",
    )
    cancelled_orders: Mapped[list[BusinessOrder]] = relationship(
        back_populates="cancelled_by",
        foreign_keys="BusinessOrder.cancelled_by_user_id",
    )
    created_dispatches: Mapped[list[Dispatch]] = relationship(back_populates="created_by")
    received_goods_receipts: Mapped[list[GoodsReceipt]] = relationship(back_populates="received_by")
    created_supplier_invoices: Mapped[list[SupplierInvoice]] = relationship(
        back_populates="created_by"
    )
    responsible_transfers: Mapped[list[InventoryTransfer]] = relationship(
        back_populates="responsible_user"
    )
    created_adjustments: Mapped[list[InventoryAdjustment]] = relationship(
        back_populates="created_by"
    )
    created_inventory_movements: Mapped[list[InventoryMovement]] = relationship(
        back_populates="created_by"
    )
    created_treasury_movements: Mapped[list[TreasuryMovement]] = relationship(
        back_populates="created_by"
    )
    uploaded_documents: Mapped[list[Document]] = relationship(back_populates="uploaded_by")
    audit_events: Mapped[list[AuditEvent]] = relationship(back_populates="user")
    report_schedules: Mapped[list[ReportSchedule]] = relationship(back_populates="created_by")
    order_step_events: Mapped[list[OrderStepEvent]] = relationship(back_populates="completed_by")


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        sa.Index("auth_sessions_token_hash_key", "token_hash", unique=True),
        sa.Index(
            "auth_sessions_user_id_revoked_at_expires_at_idx",
            "user_id",
            "revoked_at",
            "expires_at",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    token_hash: Mapped[str] = mapped_column(sa.Text)
    persistent: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    issued_at: Mapped[datetime] = created_at_col()
    last_seen_at: Mapped[datetime | None] = timestamptz_col()
    expires_at: Mapped[datetime] = timestamptz_col()
    revoked_at: Mapped[datetime | None] = timestamptz_col()
    ip: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(sa.Text)

    user: Mapped[User] = relationship(back_populates="sessions")


class CompanySetting(Base):
    __tablename__ = "company_settings"
    __table_args__ = (
        sa.Index("company_settings_default_warehouse_id_idx", "default_warehouse_id"),
    )

    id: Mapped[int] = mapped_column(
        sa.SmallInteger, primary_key=True, default=1, server_default=sa.text("1")
    )
    tax_id: Mapped[str] = mapped_column(sa.String(24))
    legal_name: Mapped[str] = mapped_column(sa.String(200))
    fiscal_address: Mapped[str | None] = mapped_column(sa.Text)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), default="PEN", server_default=sa.text("'PEN'")
    )
    time_zone: Mapped[str] = mapped_column(
        sa.String(64), default="America/Lima", server_default=sa.text("'America/Lima'")
    )
    invoice_series: Mapped[str] = mapped_column(sa.String(12))
    receipt_series: Mapped[str] = mapped_column(sa.String(12))
    dispatch_series: Mapped[str] = mapped_column(sa.String(12))
    credit_note_series: Mapped[str] = mapped_column(sa.String(12))
    auto_tax_submission: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    email_documents: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        sa.Numeric(5, 4), default=Decimal("0.18"), server_default=sa.text("0.18")
    )
    prices_include_tax: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    max_discount_pct: Mapped[Decimal] = mapped_column(
        sa.Numeric(5, 2), default=Decimal("5"), server_default=sa.text("5")
    )
    quotation_validity_days: Mapped[int] = mapped_column(
        sa.SmallInteger, default=14, server_default=sa.text("14")
    )
    cost_method: Mapped[CostMethod] = mapped_column(
        sa.Enum(CostMethod, name="cost_method"),
        default=CostMethod.WEIGHTED_AVERAGE,
        server_default=sa.text("'WEIGHTED_AVERAGE'"),
    )
    default_warehouse_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    allow_negative_stock: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    reorder_alerts_enabled: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    session_duration_hours: Mapped[int] = mapped_column(
        sa.SmallInteger, default=8, server_default=sa.text("8")
    )
    max_login_attempts: Mapped[int] = mapped_column(
        sa.SmallInteger, default=5, server_default=sa.text("5")
    )
    mfa_required: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    audit_retention_years: Mapped[int] = mapped_column(
        sa.SmallInteger, default=5, server_default=sa.text("5")
    )
    updated_at: Mapped[datetime] = updated_at_col()

    default_warehouse: Mapped[Warehouse | None] = relationship(back_populates="default_for")
