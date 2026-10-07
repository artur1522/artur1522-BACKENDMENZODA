"""Modelos SQLAlchemy: importarlos registra todas las tablas en Base.metadata."""

from app.models.audit import AuditEvent
from app.models.catalog import (
    Customer,
    Driver,
    Product,
    ProductCategory,
    Supplier,
    Vehicle,
    Warehouse,
)
from app.models.documents import Document, DocumentSequence, ReportSchedule
from app.models.finance import BankAccount, TreasuryMovement
from app.models.identity import (
    AuthSession,
    CompanySetting,
    Permission,
    Role,
    RolePermission,
    User,
)
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
    OrderStepEvent,
    Quotation,
    QuotationLine,
    SalesInvoice,
)

__all__ = [
    "AuditEvent",
    "AuthSession",
    "BankAccount",
    "BusinessOrder",
    "CompanySetting",
    "Customer",
    "Dispatch",
    "Document",
    "DocumentSequence",
    "Driver",
    "GoodsReceipt",
    "InventoryAdjustment",
    "InventoryMovement",
    "InventoryTransfer",
    "InventoryTransferLine",
    "OrderLine",
    "OrderStepEvent",
    "Permission",
    "Product",
    "ProductCategory",
    "PurchaseRequest",
    "PurchaseRequestLine",
    "Quotation",
    "QuotationLine",
    "ReportSchedule",
    "Role",
    "RolePermission",
    "SalesInvoice",
    "Supplier",
    "SupplierInvoice",
    "TreasuryMovement",
    "User",
    "Vehicle",
    "Warehouse",
]
