"""Espejo exacto de los enums de schema.prisma (tipos nativos de PostgreSQL).

Los nombres de miembro y de valor coinciden con los valores persistidos por Prisma
(p. ej. RecordStatus.ACTIVE -> 'ACTIVE' en la columna/enum de PG).
"""

from enum import StrEnum


class RoleType(StrEnum):
    SYSTEM = "SYSTEM"
    CUSTOM = "CUSTOM"


class UserStatus(StrEnum):
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    INACTIVE = "INACTIVE"


class IdentificationType(StrEnum):
    RUC = "RUC"
    DNI = "DNI"
    CE = "CE"


class RecordStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class WarehouseType(StrEnum):
    MAIN = "MAIN"
    SECONDARY = "SECONDARY"
    TRANSIT = "TRANSIT"


class QuotationStatus(StrEnum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    APPROVED = "APPROVED"
    CONVERTED = "CONVERTED"
    REJECTED = "REJECTED"


class PurchaseRequestStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ATTENDED = "ATTENDED"
    REJECTED = "REJECTED"


class RequestPriority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BusinessOrderKind(StrEnum):
    SALE = "SALE"
    PURCHASE = "PURCHASE"


class DispatchReason(StrEnum):
    SALE = "SALE"
    SALE_CONFIRMATION_PENDING = "SALE_CONFIRMATION_PENDING"


class GoodsCondition(StrEnum):
    CONFORMING = "CONFORMING"
    OBSERVATIONS = "OBSERVATIONS"


class SalesDocumentType(StrEnum):
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"
    CREDIT_NOTE = "CREDIT_NOTE"


class TaxSubmissionStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    VOIDED = "VOIDED"


class SupplierInvoiceValidationStatus(StrEnum):
    MATCHES_ORDER_RECEIPT = "MATCHES_ORDER_RECEIPT"
    HAS_DIFFERENCES = "HAS_DIFFERENCES"


class TransferStatus(StrEnum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class AdjustmentType(StrEnum):
    LOSS = "LOSS"
    SURPLUS = "SURPLUS"
    EXPIRY = "EXPIRY"
    CORRECTION = "CORRECTION"


class InventoryMovementType(StrEnum):
    RECEIPT = "RECEIPT"
    DISPATCH = "DISPATCH"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"


class MovementLeg(StrEnum):
    OUT = "OUT"
    IN = "IN"


class TreasuryChannel(StrEnum):
    CASH = "CASH"
    BANK = "BANK"


class TreasuryMovementType(StrEnum):
    COLLECTION = "COLLECTION"
    PAYMENT = "PAYMENT"
    OPENING = "OPENING"
    BANK_FEE = "BANK_FEE"
    MANUAL_INCOME = "MANUAL_INCOME"
    MANUAL_EXPENSE = "MANUAL_EXPENSE"


class PaymentMethod(StrEnum):
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"
    CHEQUE = "CHEQUE"
    CASH = "CASH"
    YAPE = "YAPE"
    PLIN = "PLIN"
    POS = "POS"


class ReconciliationStatus(StrEnum):
    PENDING = "PENDING"
    RECONCILED = "RECONCILED"


class DocumentCategory(StrEnum):
    INVOICE = "INVOICE"
    CONTRACT = "CONTRACT"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    DISPATCH_GUIDE = "DISPATCH_GUIDE"
    OTHER = "OTHER"
    ATTACHMENT = "ATTACHMENT"


class AuditAction(StrEnum):
    LOGIN = "LOGIN"
    CREATE = "CREATE"
    EDIT = "EDIT"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    DOWNLOAD = "DOWNLOAD"


class AuditResult(StrEnum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DENIED = "DENIED"


class ReportFrequency(StrEnum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class CostMethod(StrEnum):
    WEIGHTED_AVERAGE = "WEIGHTED_AVERAGE"
