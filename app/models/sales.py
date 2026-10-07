"""Ventas: cotizaciones, órdenes de negocio, líneas, hitos, despachos y facturas."""

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
    BusinessOrderKind,
    DispatchReason,
    QuotationStatus,
    SalesDocumentType,
    TaxSubmissionStatus,
)

if TYPE_CHECKING:
    from app.models.catalog import Customer, Driver, Product, Supplier, Vehicle, Warehouse
    from app.models.documents import Document
    from app.models.finance import TreasuryMovement
    from app.models.identity import User
    from app.models.inventory import InventoryMovement
    from app.models.purchases import GoodsReceipt, PurchaseRequest, SupplierInvoice


class Quotation(Base):
    __tablename__ = "quotations"
    __table_args__ = (
        sa.Index("quotations_code_key", "code", unique=True),
        sa.Index("quotations_customer_id_created_at_idx", "customer_id", "created_at"),
        sa.Index("quotations_status_valid_until_idx", "status", "valid_until"),
        sa.Index("quotations_seller_user_id_idx", "seller_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(24))
    customer_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    seller_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()
    valid_until: Mapped[date | None] = mapped_column(sa.Date)
    payment_terms_days: Mapped[int] = mapped_column(
        sa.SmallInteger, default=0, server_default=sa.text("0")
    )
    warehouse_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    accepted_contact_snapshot: Mapped[str | None] = mapped_column(sa.String(160))
    status: Mapped[QuotationStatus] = mapped_column(
        sa.Enum(QuotationStatus, name="quotation_status"),
        default=QuotationStatus.DRAFT,
        server_default=sa.text("'DRAFT'"),
    )
    rejected_reason: Mapped[str | None] = mapped_column(sa.Text)
    updated_at: Mapped[datetime] = updated_at_col()

    customer: Mapped[Customer] = relationship(back_populates="quotations")
    seller: Mapped[User | None] = relationship(back_populates="quotations")
    warehouse: Mapped[Warehouse | None] = relationship(back_populates="quotations")
    lines: Mapped[list[QuotationLine]] = relationship(back_populates="quotation")
    business_order: Mapped[BusinessOrder | None] = relationship(back_populates="quotation")


class QuotationLine(Base):
    __tablename__ = "quotation_lines"
    __table_args__ = (
        sa.Index("quotation_lines_product_id_idx", "product_id"),
        sa.Index(
            "quotation_lines_quotation_id_line_no_key",
            "quotation_id",
            "line_no",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    quotation_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("quotations.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    line_no: Mapped[int] = mapped_column(sa.SmallInteger)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("products.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    sku_snapshot: Mapped[str] = mapped_column(sa.String(64))
    name_snapshot: Mapped[str] = mapped_column(sa.String(200))
    unit_snapshot: Mapped[str] = mapped_column(sa.String(24))
    quantity: Mapped[Decimal] = mapped_column(sa.Numeric(14, 3))
    unit_price: Mapped[Decimal] = mapped_column(sa.Numeric(14, 6))
    created_at: Mapped[datetime] = created_at_col()

    quotation: Mapped[Quotation] = relationship(back_populates="lines")
    product: Mapped[Product | None] = relationship(back_populates="quotation_lines")


class BusinessOrder(Base):
    __tablename__ = "business_orders"
    __table_args__ = (
        sa.Index("business_orders_code_key", "code", unique=True),
        sa.Index("business_orders_quotation_id_key", "quotation_id", unique=True),
        sa.Index("business_orders_purchase_request_id_key", "purchase_request_id", unique=True),
        sa.Index("business_orders_kind_created_at_idx", "kind", "created_at"),
        sa.Index("business_orders_customer_id_created_at_idx", "customer_id", "created_at"),
        sa.Index("business_orders_supplier_id_created_at_idx", "supplier_id", "created_at"),
        sa.Index("business_orders_warehouse_id_current_step_idx", "warehouse_id", "current_step"),
        sa.Index("business_orders_seller_user_id_idx", "seller_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(24))
    kind: Mapped[BusinessOrderKind] = mapped_column(
        sa.Enum(BusinessOrderKind, name="business_order_kind")
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    quotation_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("quotations.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    purchase_request_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("purchase_requests.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    seller_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    party_name: Mapped[str] = mapped_column(sa.String(200))
    party_tax_id: Mapped[str | None] = mapped_column(sa.String(24))
    party_address: Mapped[str | None] = mapped_column(sa.Text)
    party_contact: Mapped[str | None] = mapped_column(sa.String(200))
    party_email: Mapped[str | None] = mapped_column(sa.String(254))
    payment_terms_days: Mapped[int] = mapped_column(
        sa.SmallInteger, default=0, server_default=sa.text("0")
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        sa.Numeric(5, 4), default=Decimal("0.18"), server_default=sa.text("0.18")
    )
    current_step: Mapped[int] = mapped_column(
        sa.SmallInteger, default=1, server_default=sa.text("1")
    )
    is_cancelled: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, server_default=sa.text("false")
    )
    cancelled_at: Mapped[datetime | None] = timestamptz_col()
    cancelled_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    customer: Mapped[Customer | None] = relationship(back_populates="orders")
    supplier: Mapped[Supplier | None] = relationship(back_populates="orders")
    quotation: Mapped[Quotation | None] = relationship(back_populates="business_order")
    purchase_request: Mapped[PurchaseRequest | None] = relationship(back_populates="business_order")
    warehouse: Mapped[Warehouse] = relationship(back_populates="orders")
    seller: Mapped[User | None] = relationship(
        back_populates="sold_orders", foreign_keys=[seller_user_id]
    )
    created_by: Mapped[User | None] = relationship(
        back_populates="created_orders", foreign_keys=[created_by_user_id]
    )
    cancelled_by: Mapped[User | None] = relationship(
        back_populates="cancelled_orders", foreign_keys=[cancelled_by_user_id]
    )
    lines: Mapped[list[OrderLine]] = relationship(back_populates="order")
    step_events: Mapped[list[OrderStepEvent]] = relationship(back_populates="order")
    dispatch: Mapped[Dispatch | None] = relationship(back_populates="order")
    goods_receipt: Mapped[GoodsReceipt | None] = relationship(back_populates="order")
    sales_invoice: Mapped[SalesInvoice | None] = relationship(back_populates="order")
    supplier_invoice: Mapped[SupplierInvoice | None] = relationship(back_populates="order")
    documents: Mapped[list[Document]] = relationship(back_populates="related_order")


class OrderLine(Base):
    __tablename__ = "order_lines"
    __table_args__ = (
        sa.Index("order_lines_product_id_order_id_idx", "product_id", "order_id"),
        sa.Index("order_lines_order_id_line_no_key", "order_id", "line_no", unique=True),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    line_no: Mapped[int] = mapped_column(sa.SmallInteger)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("products.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    sku_snapshot: Mapped[str] = mapped_column(sa.String(64))
    name_snapshot: Mapped[str] = mapped_column(sa.String(200))
    unit_snapshot: Mapped[str] = mapped_column(sa.String(24))
    quantity: Mapped[Decimal] = mapped_column(sa.Numeric(14, 3))
    unit_price: Mapped[Decimal] = mapped_column(sa.Numeric(14, 6))
    created_at: Mapped[datetime] = created_at_col()

    order: Mapped[BusinessOrder] = relationship(back_populates="lines")
    product: Mapped[Product | None] = relationship(back_populates="order_lines")
    inventory_movements: Mapped[list[InventoryMovement]] = relationship(back_populates="order_line")


class OrderStepEvent(Base):
    __tablename__ = "order_step_events"
    __table_args__ = (
        sa.Index(
            "order_step_events_completed_by_user_id_completed_at_idx",
            "completed_by_user_id",
            "completed_at",
        ),
        sa.Index("order_step_events_order_id_step_no_key", "order_id", "step_no", unique=True),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    step_no: Mapped[int] = mapped_column(sa.SmallInteger)
    completed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    completed_at: Mapped[datetime] = timestamptz_col()
    generated_reference: Mapped[str | None] = mapped_column(sa.String(80))
    note: Mapped[str | None] = mapped_column(sa.Text)

    order: Mapped[BusinessOrder] = relationship(back_populates="step_events")
    completed_by: Mapped[User | None] = relationship(back_populates="order_step_events")


class Dispatch(Base):
    __tablename__ = "dispatches"
    __table_args__ = (
        sa.Index("dispatches_order_id_key", "order_id", unique=True),
        sa.Index("dispatches_dispatch_number_key", "dispatch_number", unique=True),
        sa.Index("dispatches_warehouse_id_dispatched_at_idx", "warehouse_id", "dispatched_at"),
        sa.Index("dispatches_carrier_supplier_id_idx", "carrier_supplier_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    dispatch_number: Mapped[str] = mapped_column(sa.String(40))
    dispatched_at: Mapped[datetime] = timestamptz_col()
    reason: Mapped[DispatchReason] = mapped_column(sa.Enum(DispatchReason, name="dispatch_reason"))
    carrier_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("vehicles.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("drivers.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    destination_snapshot: Mapped[str] = mapped_column(sa.Text)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()

    order: Mapped[BusinessOrder] = relationship(back_populates="dispatch")
    carrier: Mapped[Supplier | None] = relationship(back_populates="dispatches")
    vehicle: Mapped[Vehicle | None] = relationship(back_populates="dispatches")
    driver: Mapped[Driver | None] = relationship(back_populates="dispatches")
    warehouse: Mapped[Warehouse] = relationship(back_populates="dispatches")
    created_by: Mapped[User | None] = relationship(back_populates="created_dispatches")
    inventory_movements: Mapped[list[InventoryMovement]] = relationship(back_populates="dispatch")


class SalesInvoice(Base):
    __tablename__ = "sales_invoices"
    __table_args__ = (
        sa.Index("sales_invoices_order_id_key", "order_id", unique=True),
        sa.Index("sales_invoices_series_number_key", "series", "number", unique=True),
        sa.Index("sales_invoices_customer_id_due_at_idx", "customer_id", "due_at"),
        sa.Index("sales_invoices_tax_status_issued_at_idx", "tax_status", "issued_at"),
        sa.Index("sales_invoices_original_invoice_id_idx", "original_invoice_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("business_orders.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    original_invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("sales_invoices.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    document_type: Mapped[SalesDocumentType] = mapped_column(
        sa.Enum(SalesDocumentType, name="sales_document_type")
    )
    series: Mapped[str] = mapped_column(sa.String(12))
    number: Mapped[str] = mapped_column(sa.String(24))
    issued_at: Mapped[date] = mapped_column(sa.Date)
    due_at: Mapped[date | None] = mapped_column(sa.Date)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), default="PEN", server_default=sa.text("'PEN'")
    )
    subtotal: Mapped[Decimal] = mapped_column(sa.Numeric(14, 2))
    tax_amount: Mapped[Decimal] = mapped_column(sa.Numeric(14, 2))
    total: Mapped[Decimal] = mapped_column(sa.Numeric(14, 2))
    tax_status: Mapped[TaxSubmissionStatus] = mapped_column(
        sa.Enum(TaxSubmissionStatus, name="tax_submission_status"),
        default=TaxSubmissionStatus.PENDING,
        server_default=sa.text("'PENDING'"),
    )
    void_reason: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = created_at_col()

    order: Mapped[BusinessOrder | None] = relationship(back_populates="sales_invoice")
    customer: Mapped[Customer] = relationship(back_populates="invoices")
    original_invoice: Mapped[SalesInvoice | None] = relationship(
        back_populates="credit_notes",
        remote_side=[id],
    )
    credit_notes: Mapped[list[SalesInvoice]] = relationship(
        back_populates="original_invoice",
    )
    treasury_movements: Mapped[list[TreasuryMovement]] = relationship(
        back_populates="sales_invoice"
    )
