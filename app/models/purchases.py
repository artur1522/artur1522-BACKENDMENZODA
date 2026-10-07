"""Compras: solicitudes con aprobación, recepción de mercadería y facturas de proveedor."""

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
    GoodsCondition,
    PurchaseRequestStatus,
    RequestPriority,
    SupplierInvoiceValidationStatus,
)

if TYPE_CHECKING:
    from app.models.catalog import Product, Supplier, Warehouse
    from app.models.finance import TreasuryMovement
    from app.models.identity import User
    from app.models.inventory import InventoryMovement
    from app.models.sales import BusinessOrder


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    __table_args__ = (
        sa.Index("purchase_requests_code_key", "code", unique=True),
        sa.Index("purchase_requests_status_required_by_idx", "status", "required_by"),
        sa.Index(
            "purchase_requests_requested_by_user_id_created_at_idx",
            "requested_by_user_id",
            "created_at",
        ),
        sa.Index("purchase_requests_reviewed_by_user_id_idx", "reviewed_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(24))
    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    requesting_area: Mapped[str] = mapped_column(sa.String(60))
    reason: Mapped[str] = mapped_column(sa.Text)
    priority: Mapped[RequestPriority] = mapped_column(
        sa.Enum(RequestPriority, name="request_priority")
    )
    required_by: Mapped[date | None] = mapped_column(sa.Date)
    warehouse_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    suggested_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    status: Mapped[PurchaseRequestStatus] = mapped_column(
        sa.Enum(PurchaseRequestStatus, name="purchase_request_status"),
        default=PurchaseRequestStatus.PENDING,
        server_default=sa.text("'PENDING'"),
    )
    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    reviewed_at: Mapped[datetime | None] = timestamptz_col()
    rejection_reason: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    requester: Mapped[User] = relationship(
        back_populates="requested_purchase_requests",
        foreign_keys=[requested_by_user_id],
    )
    reviewer: Mapped[User | None] = relationship(
        back_populates="reviewed_purchase_requests",
        foreign_keys=[reviewed_by_user_id],
    )
    warehouse: Mapped[Warehouse | None] = relationship(back_populates="purchase_requests")
    suggested_supplier: Mapped[Supplier | None] = relationship(back_populates="suggested_requests")
    lines: Mapped[list[PurchaseRequestLine]] = relationship(back_populates="purchase_request")
    business_order: Mapped[BusinessOrder | None] = relationship(back_populates="purchase_request")


class PurchaseRequestLine(Base):
    __tablename__ = "purchase_request_lines"
    __table_args__ = (
        sa.Index("purchase_request_lines_product_id_idx", "product_id"),
        sa.Index(
            "purchase_request_lines_purchase_request_id_line_no_key",
            "purchase_request_id",
            "line_no",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    purchase_request_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("purchase_requests.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    line_no: Mapped[int] = mapped_column(sa.SmallInteger)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("products.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    name_snapshot: Mapped[str] = mapped_column(sa.String(200))
    sku_snapshot: Mapped[str | None] = mapped_column(sa.String(64))
    unit_snapshot: Mapped[str] = mapped_column(sa.String(24))
    quantity: Mapped[Decimal] = mapped_column(sa.Numeric(14, 3))
    estimated_unit_cost: Mapped[Decimal] = mapped_column(sa.Numeric(14, 6))

    purchase_request: Mapped[PurchaseRequest] = relationship(back_populates="lines")
    product: Mapped[Product | None] = relationship(back_populates="request_lines")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"
    __table_args__ = (
        sa.Index("goods_receipts_order_id_key", "order_id", unique=True),
        sa.Index("goods_receipts_receipt_number_key", "receipt_number", unique=True),
        sa.Index("goods_receipts_warehouse_id_received_at_idx", "warehouse_id", "received_at"),
        sa.Index("goods_receipts_received_by_user_id_idx", "received_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    receipt_number: Mapped[str] = mapped_column(sa.String(40))
    received_at: Mapped[datetime] = timestamptz_col()
    supplier_guide_reference: Mapped[str | None] = mapped_column(sa.String(80))
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    condition: Mapped[GoodsCondition] = mapped_column(
        sa.Enum(GoodsCondition, name="goods_condition")
    )
    observations: Mapped[str | None] = mapped_column(sa.Text)
    received_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()

    order: Mapped[BusinessOrder] = relationship(back_populates="goods_receipt")
    warehouse: Mapped[Warehouse] = relationship(back_populates="goods_receipts")
    received_by: Mapped[User | None] = relationship(back_populates="received_goods_receipts")
    inventory_movements: Mapped[list[InventoryMovement]] = relationship(
        back_populates="goods_receipt"
    )


class SupplierInvoice(Base):
    __tablename__ = "supplier_invoices"
    __table_args__ = (
        sa.Index("supplier_invoices_order_id_key", "order_id", unique=True),
        sa.Index(
            "supplier_invoices_supplier_id_series_number_key",
            "supplier_id",
            "series_number",
            unique=True,
        ),
        sa.Index("supplier_invoices_supplier_id_due_at_idx", "supplier_id", "due_at"),
        sa.Index("supplier_invoices_created_by_user_id_idx", "created_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    series_number: Mapped[str] = mapped_column(sa.String(40))
    issued_at: Mapped[date] = mapped_column(sa.Date)
    due_at: Mapped[date] = mapped_column(sa.Date)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), default="PEN", server_default=sa.text("'PEN'")
    )
    total: Mapped[Decimal] = mapped_column(sa.Numeric(14, 2))
    validation_status: Mapped[SupplierInvoiceValidationStatus] = mapped_column(
        sa.Enum(
            SupplierInvoiceValidationStatus,
            name="supplier_invoice_validation_status",
        )
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()

    order: Mapped[BusinessOrder] = relationship(back_populates="supplier_invoice")
    supplier: Mapped[Supplier] = relationship(back_populates="invoices")
    created_by: Mapped[User | None] = relationship(back_populates="created_supplier_invoices")
    treasury_movements: Mapped[list[TreasuryMovement]] = relationship(
        back_populates="supplier_invoice"
    )
