"""Inventario: transferencias entre almacenes, ajustes y movimientos de stock."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._common import created_at_col, timestamptz_col, updated_at_col, uuid_pk
from app.models.enums import (
    AdjustmentType,
    InventoryMovementType,
    MovementLeg,
    TransferStatus,
)

if TYPE_CHECKING:
    from app.models.catalog import Product, Warehouse
    from app.models.identity import User
    from app.models.purchases import GoodsReceipt
    from app.models.sales import Dispatch, OrderLine


class InventoryTransfer(Base):
    __tablename__ = "inventory_transfers"
    __table_args__ = (
        sa.Index("inventory_transfers_code_key", "code", unique=True),
        sa.Index("inventory_transfers_status_created_at_idx", "status", "created_at"),
        sa.Index(
            "inventory_transfers_source_warehouse_id_created_at_idx",
            "source_warehouse_id",
            "created_at",
        ),
        sa.Index(
            "inventory_transfers_destination_warehouse_id_created_at_idx",
            "destination_warehouse_id",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(24))
    created_at: Mapped[datetime] = created_at_col()
    source_warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    destination_warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    status: Mapped[TransferStatus] = mapped_column(
        sa.Enum(TransferStatus, name="transfer_status"),
        default=TransferStatus.PENDING,
        server_default=sa.text("'PENDING'"),
    )
    dispatched_at: Mapped[datetime | None] = timestamptz_col()
    received_at: Mapped[datetime | None] = timestamptz_col()
    updated_at: Mapped[datetime] = updated_at_col()

    source_warehouse: Mapped[Warehouse] = relationship(
        back_populates="transfers_from",
        foreign_keys=[source_warehouse_id],
    )
    destination_warehouse: Mapped[Warehouse] = relationship(
        back_populates="transfers_to",
        foreign_keys=[destination_warehouse_id],
    )
    responsible_user: Mapped[User | None] = relationship(back_populates="responsible_transfers")
    lines: Mapped[list[InventoryTransferLine]] = relationship(back_populates="transfer")


class InventoryTransferLine(Base):
    __tablename__ = "inventory_transfer_lines"
    __table_args__ = (
        sa.Index("inventory_transfer_lines_product_id_idx", "product_id"),
        sa.Index(
            "inventory_transfer_lines_transfer_id_line_no_key",
            "transfer_id",
            "line_no",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    transfer_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("inventory_transfers.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    line_no: Mapped[int] = mapped_column(sa.SmallInteger)
    product_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("products.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    sku_snapshot: Mapped[str] = mapped_column(sa.String(64))
    name_snapshot: Mapped[str] = mapped_column(sa.String(200))
    unit_snapshot: Mapped[str] = mapped_column(sa.String(24))
    quantity: Mapped[Decimal] = mapped_column(sa.Numeric(14, 3))

    transfer: Mapped[InventoryTransfer] = relationship(back_populates="lines")
    product: Mapped[Product] = relationship(back_populates="transfer_lines")
    inventory_movements: Mapped[list[InventoryMovement]] = relationship(
        back_populates="transfer_line"
    )


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"
    __table_args__ = (
        sa.Index("inventory_adjustments_code_key", "code", unique=True),
        sa.Index(
            "inventory_adjustments_product_id_warehouse_id_created_at_idx",
            "product_id",
            "warehouse_id",
            "created_at",
        ),
        sa.Index("inventory_adjustments_created_by_user_id_idx", "created_by_user_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(sa.String(24))
    product_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("products.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    adjustment_type: Mapped[AdjustmentType] = mapped_column(
        sa.Enum(AdjustmentType, name="adjustment_type")
    )
    reason: Mapped[str] = mapped_column(sa.Text)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()

    product: Mapped[Product] = relationship(back_populates="adjustments")
    warehouse: Mapped[Warehouse] = relationship(back_populates="adjustments")
    created_by: Mapped[User | None] = relationship(back_populates="created_adjustments")
    inventory_movement: Mapped[InventoryMovement | None] = relationship(back_populates="adjustment")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        sa.Index("inventory_movements_adjustment_id_key", "adjustment_id", unique=True),
        sa.Index(
            "inventory_movements_product_id_warehouse_id_occurred_at_id_idx",
            "product_id",
            "warehouse_id",
            "occurred_at",
            "id",
        ),
        sa.Index("inventory_movements_warehouse_id_occurred_at_idx", "warehouse_id", "occurred_at"),
        sa.Index("inventory_movements_order_line_id_idx", "order_line_id"),
        sa.Index("inventory_movements_dispatch_id_idx", "dispatch_id"),
        sa.Index("inventory_movements_goods_receipt_id_idx", "goods_receipt_id"),
        sa.Index("inventory_movements_transfer_line_id_idx", "transfer_line_id"),
        sa.Index("inventory_movements_created_by_user_id_idx", "created_by_user_id"),
        sa.Index(
            "inventory_movements_transfer_line_id_movement_leg_key",
            "transfer_line_id",
            "movement_leg",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    occurred_at: Mapped[datetime] = timestamptz_col()
    product_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("products.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("warehouses.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    movement_type: Mapped[InventoryMovementType] = mapped_column(
        sa.Enum(InventoryMovementType, name="inventory_movement_type")
    )
    quantity_delta: Mapped[Decimal] = mapped_column(sa.Numeric(14, 3))
    unit_cost: Mapped[Decimal] = mapped_column(sa.Numeric(14, 6))
    order_line_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("order_lines.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    dispatch_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("dispatches.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    goods_receipt_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("goods_receipts.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    transfer_line_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("inventory_transfer_lines.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    adjustment_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("inventory_adjustments.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    movement_leg: Mapped[MovementLeg | None] = mapped_column(
        sa.Enum(MovementLeg, name="movement_leg")
    )
    reference_snapshot: Mapped[str] = mapped_column(sa.String(80))
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = created_at_col()

    product: Mapped[Product] = relationship(back_populates="inventory_movements")
    warehouse: Mapped[Warehouse] = relationship(back_populates="inventory_movements")
    order_line: Mapped[OrderLine | None] = relationship(back_populates="inventory_movements")
    dispatch: Mapped[Dispatch | None] = relationship(back_populates="inventory_movements")
    goods_receipt: Mapped[GoodsReceipt | None] = relationship(back_populates="inventory_movements")
    transfer_line: Mapped[InventoryTransferLine | None] = relationship(
        back_populates="inventory_movements"
    )
    adjustment: Mapped[InventoryAdjustment | None] = relationship(
        back_populates="inventory_movement"
    )
    created_by: Mapped[User | None] = relationship(back_populates="created_inventory_movements")
