"""Catálogo maestro: clientes, proveedores, productos, almacenes y logística."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import created_at_col, updated_at_col, uuid_pk
from app.models.enums import IdentificationType, RecordStatus, WarehouseType

if TYPE_CHECKING:
    from app.models.documents import Document
    from app.models.identity import CompanySetting, User
    from app.models.inventory import (
        InventoryAdjustment,
        InventoryMovement,
        InventoryTransfer,
        InventoryTransferLine,
    )
    from app.models.purchases import (
        GoodsReceipt,
        PurchaseRequest,
        PurchaseRequestLine,
        SupplierInvoice,
    )
    from app.models.sales import (
        BusinessOrder,
        Dispatch,
        OrderLine,
        Quotation,
        QuotationLine,
        SalesInvoice,
    )


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        sa.Index("customers_code_key", "code", unique=True),
        sa.Index(
            "customers_document_type_document_number_key",
            "document_type",
            "document_number",
            unique=True,
        ),
        sa.Index("customers_status_idx", "status"),
        sa.Index("customers_salesperson_user_id_idx", "salesperson_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(20))
    legal_name: Mapped[str] = mapped_column(sa.String(200))
    document_type: Mapped[IdentificationType] = mapped_column(
        sa.Enum(IdentificationType, name="identification_type")
    )
    document_number: Mapped[str] = mapped_column(sa.String(24))
    contact_name: Mapped[str | None] = mapped_column(sa.String(160))
    phone: Mapped[str | None] = mapped_column(sa.String(40))
    billing_email: Mapped[str | None] = mapped_column(sa.String(254))
    fiscal_address: Mapped[str | None] = mapped_column(sa.Text)
    payment_terms_days: Mapped[int] = mapped_column(
        sa.SmallInteger, default=0, server_default=sa.text("0")
    )
    credit_limit: Mapped[Decimal] = mapped_column(
        sa.Numeric(14, 2), default=Decimal("0"), server_default=sa.text("0")
    )
    salesperson_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    salesperson: Mapped[User | None] = relationship(back_populates="assigned_customers")
    quotations: Mapped[list[Quotation]] = relationship(back_populates="customer")
    orders: Mapped[list[BusinessOrder]] = relationship(back_populates="customer")
    invoices: Mapped[list[SalesInvoice]] = relationship(back_populates="customer")
    documents: Mapped[list[Document]] = relationship(back_populates="related_customer")


class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = (
        sa.Index("suppliers_code_key", "code", unique=True),
        sa.Index("suppliers_tax_id_key", "tax_id", unique=True),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(20))
    legal_name: Mapped[str] = mapped_column(sa.String(200))
    tax_id: Mapped[str] = mapped_column(sa.String(24))
    contact_name: Mapped[str | None] = mapped_column(sa.String(160))
    phone: Mapped[str | None] = mapped_column(sa.String(40))
    email: Mapped[str | None] = mapped_column(sa.String(254))
    address: Mapped[str | None] = mapped_column(sa.Text)
    business_category: Mapped[str | None] = mapped_column(sa.String(80))
    payment_terms_days: Mapped[int] = mapped_column(
        sa.SmallInteger, default=0, server_default=sa.text("0")
    )
    bank_details_label: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    primary_products: Mapped[list[Product]] = relationship(back_populates="primary_supplier")
    suggested_requests: Mapped[list[PurchaseRequest]] = relationship(
        back_populates="suggested_supplier"
    )
    orders: Mapped[list[BusinessOrder]] = relationship(back_populates="supplier")
    drivers: Mapped[list[Driver]] = relationship(back_populates="carrier")
    vehicles: Mapped[list[Vehicle]] = relationship(back_populates="carrier")
    invoices: Mapped[list[SupplierInvoice]] = relationship(back_populates="supplier")
    documents: Mapped[list[Document]] = relationship(back_populates="related_supplier")
    dispatches: Mapped[list[Dispatch]] = relationship(back_populates="carrier")


class ProductCategory(Base):
    __tablename__ = "product_categories"
    __table_args__ = (
        sa.Index("product_categories_code_key", "code", unique=True),
        sa.Index("product_categories_name_key", "name", unique=True),
        sa.Index("product_categories_parent_category_id_idx", "parent_category_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(20))
    name: Mapped[str] = mapped_column(sa.String(120))
    description: Mapped[str | None] = mapped_column(sa.Text)
    parent_category_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("product_categories.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    target_margin_pct: Mapped[Decimal | None] = mapped_column(sa.Numeric(5, 2))
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )

    parent: Mapped[ProductCategory | None] = relationship(
        back_populates="children", remote_side=[id]
    )
    children: Mapped[list[ProductCategory]] = relationship(back_populates="parent")
    products: Mapped[list[Product]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        sa.Index("products_sku_key", "sku", unique=True),
        sa.Index("products_category_id_status_idx", "category_id", "status"),
        sa.Index("products_primary_supplier_id_idx", "primary_supplier_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    sku: Mapped[str] = mapped_column(sa.String(64))
    name: Mapped[str] = mapped_column(sa.String(200))
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("product_categories.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    unit: Mapped[str] = mapped_column(sa.String(24))
    sale_price: Mapped[Decimal] = mapped_column(sa.Numeric(14, 6))
    average_cost: Mapped[Decimal] = mapped_column(
        sa.Numeric(14, 6), default=Decimal("0"), server_default=sa.text("0")
    )
    minimum_stock: Mapped[Decimal] = mapped_column(
        sa.Numeric(14, 3), default=Decimal("0"), server_default=sa.text("0")
    )
    primary_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    taxable: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=sa.text("true"))
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    category: Mapped[ProductCategory | None] = relationship(back_populates="products")
    primary_supplier: Mapped[Supplier | None] = relationship(back_populates="primary_products")
    quotation_lines: Mapped[list[QuotationLine]] = relationship(back_populates="product")
    request_lines: Mapped[list[PurchaseRequestLine]] = relationship(back_populates="product")
    order_lines: Mapped[list[OrderLine]] = relationship(back_populates="product")
    transfer_lines: Mapped[list[InventoryTransferLine]] = relationship(back_populates="product")
    adjustments: Mapped[list[InventoryAdjustment]] = relationship(back_populates="product")
    inventory_movements: Mapped[list[InventoryMovement]] = relationship(back_populates="product")


class Warehouse(Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        sa.Index("warehouses_code_key", "code", unique=True),
        sa.Index("warehouses_name_key", "name", unique=True),
        sa.Index("warehouses_status_idx", "status"),
        sa.Index("warehouses_manager_user_id_idx", "manager_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(20))
    name: Mapped[str] = mapped_column(sa.String(120))
    warehouse_type: Mapped[WarehouseType] = mapped_column(
        sa.Enum(WarehouseType, name="warehouse_type")
    )
    address: Mapped[str | None] = mapped_column(sa.Text)
    district: Mapped[str | None] = mapped_column(sa.String(100))
    manager_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )

    manager: Mapped[User | None] = relationship(back_populates="managed_warehouses")
    quotations: Mapped[list[Quotation]] = relationship(back_populates="warehouse")
    purchase_requests: Mapped[list[PurchaseRequest]] = relationship(back_populates="warehouse")
    orders: Mapped[list[BusinessOrder]] = relationship(back_populates="warehouse")
    dispatches: Mapped[list[Dispatch]] = relationship(back_populates="warehouse")
    goods_receipts: Mapped[list[GoodsReceipt]] = relationship(back_populates="warehouse")
    transfers_from: Mapped[list[InventoryTransfer]] = relationship(
        back_populates="source_warehouse",
        foreign_keys="InventoryTransfer.source_warehouse_id",
    )
    transfers_to: Mapped[list[InventoryTransfer]] = relationship(
        back_populates="destination_warehouse",
        foreign_keys="InventoryTransfer.destination_warehouse_id",
    )
    adjustments: Mapped[list[InventoryAdjustment]] = relationship(back_populates="warehouse")
    inventory_movements: Mapped[list[InventoryMovement]] = relationship(back_populates="warehouse")
    default_for: Mapped[list[CompanySetting]] = relationship(back_populates="default_warehouse")


class Driver(Base):
    __tablename__ = "drivers"
    __table_args__ = (
        sa.Index("drivers_code_key", "code", unique=True),
        sa.Index("drivers_national_id_key", "national_id", unique=True),
        sa.Index("drivers_license_number_key", "license_number", unique=True),
        sa.Index("drivers_carrier_supplier_id_status_idx", "carrier_supplier_id", "status"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(20))
    full_name: Mapped[str] = mapped_column(sa.String(160))
    national_id: Mapped[str] = mapped_column(sa.String(24))
    phone: Mapped[str | None] = mapped_column(sa.String(40))
    license_number: Mapped[str] = mapped_column(sa.String(40))
    license_category: Mapped[str] = mapped_column(sa.String(16))
    is_company_driver: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    carrier_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    carrier: Mapped[Supplier | None] = relationship(back_populates="drivers")
    default_vehicles: Mapped[list[Vehicle]] = relationship(back_populates="default_driver")
    dispatches: Mapped[list[Dispatch]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        sa.Index("vehicles_plate_key", "plate", unique=True),
        sa.Index("vehicles_carrier_supplier_id_status_idx", "carrier_supplier_id", "status"),
        sa.Index("vehicles_default_driver_id_idx", "default_driver_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    plate: Mapped[str] = mapped_column(sa.String(16))
    vehicle_type: Mapped[str] = mapped_column(sa.String(32))
    brand: Mapped[str | None] = mapped_column(sa.String(80))
    model: Mapped[str | None] = mapped_column(sa.String(80))
    capacity: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 3))
    capacity_unit: Mapped[str | None] = mapped_column(sa.String(12))
    is_company_vehicle: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, server_default=sa.text("true")
    )
    carrier_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("suppliers.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    default_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("drivers.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    status: Mapped[RecordStatus] = mapped_column(
        sa.Enum(RecordStatus, name="record_status"),
        default=RecordStatus.ACTIVE,
        server_default=sa.text("'ACTIVE'"),
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    carrier: Mapped[Supplier | None] = relationship(back_populates="vehicles")
    default_driver: Mapped[Driver | None] = relationship(back_populates="default_vehicles")
    dispatches: Mapped[list[Dispatch]] = relationship(back_populates="vehicle")
