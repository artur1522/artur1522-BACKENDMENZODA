-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "citext";

-- CreateEnum
CREATE TYPE "role_type" AS ENUM ('SYSTEM', 'CUSTOM');

-- CreateEnum
CREATE TYPE "user_status" AS ENUM ('INVITED', 'ACTIVE', 'LOCKED', 'INACTIVE');

-- CreateEnum
CREATE TYPE "identification_type" AS ENUM ('RUC', 'DNI', 'CE');

-- CreateEnum
CREATE TYPE "record_status" AS ENUM ('ACTIVE', 'INACTIVE');

-- CreateEnum
CREATE TYPE "warehouse_type" AS ENUM ('MAIN', 'SECONDARY', 'TRANSIT');

-- CreateEnum
CREATE TYPE "quotation_status" AS ENUM ('DRAFT', 'SENT', 'APPROVED', 'CONVERTED', 'REJECTED');

-- CreateEnum
CREATE TYPE "purchase_request_status" AS ENUM ('PENDING', 'APPROVED', 'ATTENDED', 'REJECTED');

-- CreateEnum
CREATE TYPE "request_priority" AS ENUM ('HIGH', 'MEDIUM', 'LOW');

-- CreateEnum
CREATE TYPE "business_order_kind" AS ENUM ('SALE', 'PURCHASE');

-- CreateEnum
CREATE TYPE "dispatch_reason" AS ENUM ('SALE', 'SALE_CONFIRMATION_PENDING');

-- CreateEnum
CREATE TYPE "goods_condition" AS ENUM ('CONFORMING', 'OBSERVATIONS');

-- CreateEnum
CREATE TYPE "sales_document_type" AS ENUM ('INVOICE', 'RECEIPT', 'CREDIT_NOTE');

-- CreateEnum
CREATE TYPE "tax_submission_status" AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'VOIDED');

-- CreateEnum
CREATE TYPE "supplier_invoice_validation_status" AS ENUM ('MATCHES_ORDER_RECEIPT', 'HAS_DIFFERENCES');

-- CreateEnum
CREATE TYPE "transfer_status" AS ENUM ('PENDING', 'IN_TRANSIT', 'RECEIVED', 'CANCELLED');

-- CreateEnum
CREATE TYPE "adjustment_type" AS ENUM ('LOSS', 'SURPLUS', 'EXPIRY', 'CORRECTION');

-- CreateEnum
CREATE TYPE "inventory_movement_type" AS ENUM ('RECEIPT', 'DISPATCH', 'TRANSFER', 'ADJUSTMENT');

-- CreateEnum
CREATE TYPE "movement_leg" AS ENUM ('OUT', 'IN');

-- CreateEnum
CREATE TYPE "treasury_channel" AS ENUM ('CASH', 'BANK');

-- CreateEnum
CREATE TYPE "treasury_movement_type" AS ENUM ('COLLECTION', 'PAYMENT', 'OPENING', 'BANK_FEE', 'MANUAL_INCOME', 'MANUAL_EXPENSE');

-- CreateEnum
CREATE TYPE "payment_method" AS ENUM ('TRANSFER', 'DEPOSIT', 'CHEQUE', 'CASH', 'YAPE', 'PLIN', 'POS');

-- CreateEnum
CREATE TYPE "reconciliation_status" AS ENUM ('PENDING', 'RECONCILED');

-- CreateEnum
CREATE TYPE "document_category" AS ENUM ('INVOICE', 'CONTRACT', 'PURCHASE_ORDER', 'DISPATCH_GUIDE', 'OTHER', 'ATTACHMENT');

-- CreateEnum
CREATE TYPE "audit_action" AS ENUM ('LOGIN', 'CREATE', 'EDIT', 'DELETE', 'EXPORT', 'DOWNLOAD');

-- CreateEnum
CREATE TYPE "audit_result" AS ENUM ('SUCCESS', 'FAILURE', 'DENIED');

-- CreateEnum
CREATE TYPE "report_frequency" AS ENUM ('DAILY', 'WEEKLY', 'MONTHLY');

-- CreateEnum
CREATE TYPE "cost_method" AS ENUM ('WEIGHTED_AVERAGE');

-- CreateTable
CREATE TABLE "roles" (
    "id" UUID NOT NULL,
    "code" VARCHAR(40) NOT NULL,
    "name" VARCHAR(80) NOT NULL,
    "description" TEXT,
    "role_type" "role_type" NOT NULL DEFAULT 'CUSTOM',
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "permissions" (
    "id" UUID NOT NULL,
    "module_key" VARCHAR(80) NOT NULL,
    "action_key" VARCHAR(16) NOT NULL,

    CONSTRAINT "permissions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "role_permissions" (
    "role_id" UUID NOT NULL,
    "permission_id" UUID NOT NULL,
    "granted" BOOLEAN NOT NULL DEFAULT false,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("role_id","permission_id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" UUID NOT NULL,
    "role_id" UUID NOT NULL,
    "full_name" VARCHAR(160) NOT NULL,
    "email" CITEXT NOT NULL,
    "password_hash" TEXT,
    "area" VARCHAR(60),
    "status" "user_status" NOT NULL DEFAULT 'INVITED',
    "mfa_enabled" BOOLEAN NOT NULL DEFAULT false,
    "failed_login_attempts" SMALLINT NOT NULL DEFAULT 0,
    "locked_until" TIMESTAMPTZ(6),
    "last_login_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_sessions" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "token_hash" TEXT NOT NULL,
    "persistent" BOOLEAN NOT NULL DEFAULT true,
    "issued_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_seen_at" TIMESTAMPTZ(6),
    "expires_at" TIMESTAMPTZ(6) NOT NULL,
    "revoked_at" TIMESTAMPTZ(6),
    "ip" INET,
    "user_agent" TEXT,

    CONSTRAINT "auth_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "customers" (
    "id" UUID NOT NULL,
    "code" VARCHAR(20) NOT NULL,
    "legal_name" VARCHAR(200) NOT NULL,
    "document_type" "identification_type" NOT NULL,
    "document_number" VARCHAR(24) NOT NULL,
    "contact_name" VARCHAR(160),
    "phone" VARCHAR(40),
    "billing_email" VARCHAR(254),
    "fiscal_address" TEXT,
    "payment_terms_days" SMALLINT NOT NULL DEFAULT 0,
    "credit_limit" DECIMAL(14,2) NOT NULL DEFAULT 0,
    "salesperson_user_id" UUID,
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "customers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "suppliers" (
    "id" UUID NOT NULL,
    "code" VARCHAR(20) NOT NULL,
    "legal_name" VARCHAR(200) NOT NULL,
    "tax_id" VARCHAR(24) NOT NULL,
    "contact_name" VARCHAR(160),
    "phone" VARCHAR(40),
    "email" VARCHAR(254),
    "address" TEXT,
    "business_category" VARCHAR(80),
    "payment_terms_days" SMALLINT NOT NULL DEFAULT 0,
    "bank_details_label" TEXT,
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "suppliers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "product_categories" (
    "id" UUID NOT NULL,
    "code" VARCHAR(20) NOT NULL,
    "name" VARCHAR(120) NOT NULL,
    "description" TEXT,
    "parent_category_id" UUID,
    "target_margin_pct" DECIMAL(5,2),
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT "product_categories_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "products" (
    "id" UUID NOT NULL,
    "sku" VARCHAR(64) NOT NULL,
    "name" VARCHAR(200) NOT NULL,
    "category_id" UUID,
    "unit" VARCHAR(24) NOT NULL,
    "sale_price" DECIMAL(14,6) NOT NULL,
    "average_cost" DECIMAL(14,6) NOT NULL DEFAULT 0,
    "minimum_stock" DECIMAL(14,3) NOT NULL DEFAULT 0,
    "primary_supplier_id" UUID,
    "taxable" BOOLEAN NOT NULL DEFAULT true,
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "products_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "warehouses" (
    "id" UUID NOT NULL,
    "code" VARCHAR(20) NOT NULL,
    "name" VARCHAR(120) NOT NULL,
    "warehouse_type" "warehouse_type" NOT NULL,
    "address" TEXT,
    "district" VARCHAR(100),
    "manager_user_id" UUID,
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT "warehouses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "drivers" (
    "id" UUID NOT NULL,
    "code" VARCHAR(20) NOT NULL,
    "full_name" VARCHAR(160) NOT NULL,
    "national_id" VARCHAR(24) NOT NULL,
    "phone" VARCHAR(40),
    "license_number" VARCHAR(40) NOT NULL,
    "license_category" VARCHAR(16) NOT NULL,
    "is_company_driver" BOOLEAN NOT NULL DEFAULT true,
    "carrier_supplier_id" UUID,
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "drivers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "vehicles" (
    "id" UUID NOT NULL,
    "plate" VARCHAR(16) NOT NULL,
    "vehicle_type" VARCHAR(32) NOT NULL,
    "brand" VARCHAR(80),
    "model" VARCHAR(80),
    "capacity" DECIMAL(12,3),
    "capacity_unit" VARCHAR(12),
    "is_company_vehicle" BOOLEAN NOT NULL DEFAULT true,
    "carrier_supplier_id" UUID,
    "default_driver_id" UUID,
    "status" "record_status" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "vehicles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "quotations" (
    "id" UUID NOT NULL,
    "code" VARCHAR(24) NOT NULL,
    "customer_id" UUID NOT NULL,
    "seller_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "valid_until" DATE,
    "payment_terms_days" SMALLINT NOT NULL DEFAULT 0,
    "warehouse_id" UUID,
    "accepted_contact_snapshot" VARCHAR(160),
    "status" "quotation_status" NOT NULL DEFAULT 'DRAFT',
    "rejected_reason" TEXT,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "quotations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "quotation_lines" (
    "id" UUID NOT NULL,
    "quotation_id" UUID NOT NULL,
    "line_no" SMALLINT NOT NULL,
    "product_id" UUID,
    "sku_snapshot" VARCHAR(64) NOT NULL,
    "name_snapshot" VARCHAR(200) NOT NULL,
    "unit_snapshot" VARCHAR(24) NOT NULL,
    "quantity" DECIMAL(14,3) NOT NULL,
    "unit_price" DECIMAL(14,6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "quotation_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "purchase_requests" (
    "id" UUID NOT NULL,
    "code" VARCHAR(24) NOT NULL,
    "requested_by_user_id" UUID NOT NULL,
    "requesting_area" VARCHAR(60) NOT NULL,
    "reason" TEXT NOT NULL,
    "priority" "request_priority" NOT NULL,
    "required_by" DATE,
    "warehouse_id" UUID,
    "suggested_supplier_id" UUID,
    "status" "purchase_request_status" NOT NULL DEFAULT 'PENDING',
    "reviewed_by_user_id" UUID,
    "reviewed_at" TIMESTAMPTZ(6),
    "rejection_reason" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "purchase_requests_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "purchase_request_lines" (
    "id" UUID NOT NULL,
    "purchase_request_id" UUID NOT NULL,
    "line_no" SMALLINT NOT NULL,
    "product_id" UUID,
    "name_snapshot" VARCHAR(200) NOT NULL,
    "sku_snapshot" VARCHAR(64),
    "unit_snapshot" VARCHAR(24) NOT NULL,
    "quantity" DECIMAL(14,3) NOT NULL,
    "estimated_unit_cost" DECIMAL(14,6) NOT NULL,

    CONSTRAINT "purchase_request_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "business_orders" (
    "id" UUID NOT NULL,
    "code" VARCHAR(24) NOT NULL,
    "kind" "business_order_kind" NOT NULL,
    "customer_id" UUID,
    "supplier_id" UUID,
    "quotation_id" UUID,
    "purchase_request_id" UUID,
    "warehouse_id" UUID NOT NULL,
    "seller_user_id" UUID,
    "created_by_user_id" UUID,
    "party_name" VARCHAR(200) NOT NULL,
    "party_tax_id" VARCHAR(24),
    "party_address" TEXT,
    "party_contact" VARCHAR(200),
    "party_email" VARCHAR(254),
    "payment_terms_days" SMALLINT NOT NULL DEFAULT 0,
    "tax_rate" DECIMAL(5,4) NOT NULL DEFAULT 0.18,
    "current_step" SMALLINT NOT NULL DEFAULT 1,
    "is_cancelled" BOOLEAN NOT NULL DEFAULT false,
    "cancelled_at" TIMESTAMPTZ(6),
    "cancelled_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "business_orders_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "order_lines" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "line_no" SMALLINT NOT NULL,
    "product_id" UUID,
    "sku_snapshot" VARCHAR(64) NOT NULL,
    "name_snapshot" VARCHAR(200) NOT NULL,
    "unit_snapshot" VARCHAR(24) NOT NULL,
    "quantity" DECIMAL(14,3) NOT NULL,
    "unit_price" DECIMAL(14,6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "order_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "order_step_events" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "step_no" SMALLINT NOT NULL,
    "completed_by_user_id" UUID,
    "completed_at" TIMESTAMPTZ(6) NOT NULL,
    "generated_reference" VARCHAR(80),
    "note" TEXT,

    CONSTRAINT "order_step_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "dispatches" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "dispatch_number" VARCHAR(40) NOT NULL,
    "dispatched_at" TIMESTAMPTZ(6) NOT NULL,
    "reason" "dispatch_reason" NOT NULL,
    "carrier_supplier_id" UUID,
    "vehicle_id" UUID,
    "driver_id" UUID,
    "warehouse_id" UUID NOT NULL,
    "destination_snapshot" TEXT NOT NULL,
    "created_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "dispatches_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "goods_receipts" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "receipt_number" VARCHAR(40) NOT NULL,
    "received_at" TIMESTAMPTZ(6) NOT NULL,
    "supplier_guide_reference" VARCHAR(80),
    "warehouse_id" UUID NOT NULL,
    "condition" "goods_condition" NOT NULL,
    "observations" TEXT,
    "received_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "goods_receipts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_invoices" (
    "id" UUID NOT NULL,
    "order_id" UUID,
    "customer_id" UUID NOT NULL,
    "original_invoice_id" UUID,
    "document_type" "sales_document_type" NOT NULL,
    "series" VARCHAR(12) NOT NULL,
    "number" VARCHAR(24) NOT NULL,
    "issued_at" DATE NOT NULL,
    "due_at" DATE,
    "currency" CHAR(3) NOT NULL DEFAULT 'PEN',
    "subtotal" DECIMAL(14,2) NOT NULL,
    "tax_amount" DECIMAL(14,2) NOT NULL,
    "total" DECIMAL(14,2) NOT NULL,
    "tax_status" "tax_submission_status" NOT NULL DEFAULT 'PENDING',
    "void_reason" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sales_invoices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "supplier_invoices" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "supplier_id" UUID NOT NULL,
    "series_number" VARCHAR(40) NOT NULL,
    "issued_at" DATE NOT NULL,
    "due_at" DATE NOT NULL,
    "currency" CHAR(3) NOT NULL DEFAULT 'PEN',
    "total" DECIMAL(14,2) NOT NULL,
    "validation_status" "supplier_invoice_validation_status" NOT NULL,
    "created_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "supplier_invoices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "inventory_transfers" (
    "id" UUID NOT NULL,
    "code" VARCHAR(24) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "source_warehouse_id" UUID NOT NULL,
    "destination_warehouse_id" UUID NOT NULL,
    "responsible_user_id" UUID,
    "status" "transfer_status" NOT NULL DEFAULT 'PENDING',
    "dispatched_at" TIMESTAMPTZ(6),
    "received_at" TIMESTAMPTZ(6),
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "inventory_transfers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "inventory_transfer_lines" (
    "id" UUID NOT NULL,
    "transfer_id" UUID NOT NULL,
    "line_no" SMALLINT NOT NULL,
    "product_id" UUID NOT NULL,
    "sku_snapshot" VARCHAR(64) NOT NULL,
    "name_snapshot" VARCHAR(200) NOT NULL,
    "unit_snapshot" VARCHAR(24) NOT NULL,
    "quantity" DECIMAL(14,3) NOT NULL,

    CONSTRAINT "inventory_transfer_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "inventory_adjustments" (
    "id" UUID NOT NULL,
    "code" VARCHAR(24) NOT NULL,
    "product_id" UUID NOT NULL,
    "warehouse_id" UUID NOT NULL,
    "adjustment_type" "adjustment_type" NOT NULL,
    "reason" TEXT NOT NULL,
    "created_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "inventory_adjustments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "inventory_movements" (
    "id" UUID NOT NULL,
    "occurred_at" TIMESTAMPTZ(6) NOT NULL,
    "product_id" UUID NOT NULL,
    "warehouse_id" UUID NOT NULL,
    "movement_type" "inventory_movement_type" NOT NULL,
    "quantity_delta" DECIMAL(14,3) NOT NULL,
    "unit_cost" DECIMAL(14,6) NOT NULL,
    "order_line_id" UUID,
    "dispatch_id" UUID,
    "goods_receipt_id" UUID,
    "transfer_line_id" UUID,
    "adjustment_id" UUID,
    "movement_leg" "movement_leg",
    "reference_snapshot" VARCHAR(80) NOT NULL,
    "created_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "inventory_movements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bank_accounts" (
    "id" UUID NOT NULL,
    "label" VARCHAR(120) NOT NULL,
    "bank_name" VARCHAR(80),
    "account_reference" VARCHAR(80),
    "currency" CHAR(3) NOT NULL DEFAULT 'PEN',
    "opening_balance" DECIMAL(14,2) NOT NULL DEFAULT 0,
    "opening_as_of" DATE,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "bank_accounts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "treasury_movements" (
    "id" UUID NOT NULL,
    "code" VARCHAR(32) NOT NULL,
    "occurred_at" TIMESTAMPTZ(6) NOT NULL,
    "channel" "treasury_channel" NOT NULL,
    "movement_type" "treasury_movement_type" NOT NULL,
    "signed_amount" DECIMAL(14,2) NOT NULL,
    "description" TEXT NOT NULL,
    "payment_method" "payment_method",
    "operation_reference" VARCHAR(80),
    "bank_account_id" UUID,
    "sales_invoice_id" UUID,
    "supplier_invoice_id" UUID,
    "reconciliation_status" "reconciliation_status",
    "note" TEXT,
    "created_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "treasury_movements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "company_settings" (
    "id" SMALLINT NOT NULL DEFAULT 1,
    "tax_id" VARCHAR(24) NOT NULL,
    "legal_name" VARCHAR(200) NOT NULL,
    "fiscal_address" TEXT,
    "currency" CHAR(3) NOT NULL DEFAULT 'PEN',
    "time_zone" VARCHAR(64) NOT NULL DEFAULT 'America/Lima',
    "invoice_series" VARCHAR(12) NOT NULL,
    "receipt_series" VARCHAR(12) NOT NULL,
    "dispatch_series" VARCHAR(12) NOT NULL,
    "credit_note_series" VARCHAR(12) NOT NULL,
    "auto_tax_submission" BOOLEAN NOT NULL DEFAULT false,
    "email_documents" BOOLEAN NOT NULL DEFAULT false,
    "tax_rate" DECIMAL(5,4) NOT NULL DEFAULT 0.18,
    "prices_include_tax" BOOLEAN NOT NULL DEFAULT false,
    "max_discount_pct" DECIMAL(5,2) NOT NULL DEFAULT 5,
    "quotation_validity_days" SMALLINT NOT NULL DEFAULT 14,
    "cost_method" "cost_method" NOT NULL DEFAULT 'WEIGHTED_AVERAGE',
    "default_warehouse_id" UUID,
    "allow_negative_stock" BOOLEAN NOT NULL DEFAULT false,
    "reorder_alerts_enabled" BOOLEAN NOT NULL DEFAULT true,
    "session_duration_hours" SMALLINT NOT NULL DEFAULT 8,
    "max_login_attempts" SMALLINT NOT NULL DEFAULT 5,
    "mfa_required" BOOLEAN NOT NULL DEFAULT false,
    "audit_retention_years" SMALLINT NOT NULL DEFAULT 5,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "company_settings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "documents" (
    "id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "category" "document_category" NOT NULL,
    "storage_key" TEXT,
    "mime_type" VARCHAR(120),
    "byte_size" BIGINT,
    "version_label" VARCHAR(40) NOT NULL,
    "related_order_id" UUID,
    "related_customer_id" UUID,
    "related_supplier_id" UUID,
    "uploaded_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ(6),

    CONSTRAINT "documents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_events" (
    "id" UUID NOT NULL,
    "occurred_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID,
    "role_id" UUID,
    "user_name_snapshot" VARCHAR(160) NOT NULL,
    "role_name_snapshot" VARCHAR(80),
    "action" "audit_action" NOT NULL,
    "module_key" VARCHAR(80) NOT NULL,
    "entity_type" VARCHAR(80),
    "entity_id" UUID,
    "reference_snapshot" VARCHAR(120),
    "description" TEXT NOT NULL,
    "result" "audit_result" NOT NULL,
    "changes" JSONB NOT NULL DEFAULT '[]',
    "detail" TEXT,
    "ip" INET,
    "device" TEXT,
    "request_id" UUID,

    CONSTRAINT "audit_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "report_schedules" (
    "id" UUID NOT NULL,
    "report_key" VARCHAR(80) NOT NULL,
    "recipient_email" VARCHAR(254) NOT NULL,
    "frequency" "report_frequency" NOT NULL,
    "is_enabled" BOOLEAN NOT NULL DEFAULT true,
    "created_by_user_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "report_schedules_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "document_sequences" (
    "document_type" VARCHAR(32) NOT NULL,
    "fiscal_year" SMALLINT NOT NULL,
    "series" VARCHAR(12) NOT NULL DEFAULT '',
    "last_value" BIGINT NOT NULL DEFAULT 0,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "document_sequences_pkey" PRIMARY KEY ("document_type","fiscal_year","series")
);

-- CreateIndex
CREATE UNIQUE INDEX "roles_code_key" ON "roles"("code");

-- CreateIndex
CREATE UNIQUE INDEX "roles_name_key" ON "roles"("name");

-- CreateIndex
CREATE UNIQUE INDEX "permissions_module_key_action_key_key" ON "permissions"("module_key", "action_key");

-- CreateIndex
CREATE INDEX "role_permissions_permission_id_idx" ON "role_permissions"("permission_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE INDEX "users_role_id_status_idx" ON "users"("role_id", "status");

-- CreateIndex
CREATE UNIQUE INDEX "auth_sessions_token_hash_key" ON "auth_sessions"("token_hash");

-- CreateIndex
CREATE INDEX "auth_sessions_user_id_revoked_at_expires_at_idx" ON "auth_sessions"("user_id", "revoked_at", "expires_at");

-- CreateIndex
CREATE UNIQUE INDEX "customers_code_key" ON "customers"("code");

-- CreateIndex
CREATE INDEX "customers_status_idx" ON "customers"("status");

-- CreateIndex
CREATE INDEX "customers_salesperson_user_id_idx" ON "customers"("salesperson_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "customers_document_type_document_number_key" ON "customers"("document_type", "document_number");

-- CreateIndex
CREATE UNIQUE INDEX "suppliers_code_key" ON "suppliers"("code");

-- CreateIndex
CREATE UNIQUE INDEX "suppliers_tax_id_key" ON "suppliers"("tax_id");

-- CreateIndex
CREATE UNIQUE INDEX "product_categories_code_key" ON "product_categories"("code");

-- CreateIndex
CREATE UNIQUE INDEX "product_categories_name_key" ON "product_categories"("name");

-- CreateIndex
CREATE INDEX "product_categories_parent_category_id_idx" ON "product_categories"("parent_category_id");

-- CreateIndex
CREATE UNIQUE INDEX "products_sku_key" ON "products"("sku");

-- CreateIndex
CREATE INDEX "products_category_id_status_idx" ON "products"("category_id", "status");

-- CreateIndex
CREATE INDEX "products_primary_supplier_id_idx" ON "products"("primary_supplier_id");

-- CreateIndex
CREATE UNIQUE INDEX "warehouses_code_key" ON "warehouses"("code");

-- CreateIndex
CREATE UNIQUE INDEX "warehouses_name_key" ON "warehouses"("name");

-- CreateIndex
CREATE INDEX "warehouses_status_idx" ON "warehouses"("status");

-- CreateIndex
CREATE INDEX "warehouses_manager_user_id_idx" ON "warehouses"("manager_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "drivers_code_key" ON "drivers"("code");

-- CreateIndex
CREATE UNIQUE INDEX "drivers_national_id_key" ON "drivers"("national_id");

-- CreateIndex
CREATE UNIQUE INDEX "drivers_license_number_key" ON "drivers"("license_number");

-- CreateIndex
CREATE INDEX "drivers_carrier_supplier_id_status_idx" ON "drivers"("carrier_supplier_id", "status");

-- CreateIndex
CREATE UNIQUE INDEX "vehicles_plate_key" ON "vehicles"("plate");

-- CreateIndex
CREATE INDEX "vehicles_carrier_supplier_id_status_idx" ON "vehicles"("carrier_supplier_id", "status");

-- CreateIndex
CREATE INDEX "vehicles_default_driver_id_idx" ON "vehicles"("default_driver_id");

-- CreateIndex
CREATE UNIQUE INDEX "quotations_code_key" ON "quotations"("code");

-- CreateIndex
CREATE INDEX "quotations_customer_id_created_at_idx" ON "quotations"("customer_id", "created_at");

-- CreateIndex
CREATE INDEX "quotations_status_valid_until_idx" ON "quotations"("status", "valid_until");

-- CreateIndex
CREATE INDEX "quotations_seller_user_id_idx" ON "quotations"("seller_user_id");

-- CreateIndex
CREATE INDEX "quotation_lines_product_id_idx" ON "quotation_lines"("product_id");

-- CreateIndex
CREATE UNIQUE INDEX "quotation_lines_quotation_id_line_no_key" ON "quotation_lines"("quotation_id", "line_no");

-- CreateIndex
CREATE UNIQUE INDEX "purchase_requests_code_key" ON "purchase_requests"("code");

-- CreateIndex
CREATE INDEX "purchase_requests_status_required_by_idx" ON "purchase_requests"("status", "required_by");

-- CreateIndex
CREATE INDEX "purchase_requests_requested_by_user_id_created_at_idx" ON "purchase_requests"("requested_by_user_id", "created_at");

-- CreateIndex
CREATE INDEX "purchase_requests_reviewed_by_user_id_idx" ON "purchase_requests"("reviewed_by_user_id");

-- CreateIndex
CREATE INDEX "purchase_request_lines_product_id_idx" ON "purchase_request_lines"("product_id");

-- CreateIndex
CREATE UNIQUE INDEX "purchase_request_lines_purchase_request_id_line_no_key" ON "purchase_request_lines"("purchase_request_id", "line_no");

-- CreateIndex
CREATE UNIQUE INDEX "business_orders_code_key" ON "business_orders"("code");

-- CreateIndex
CREATE UNIQUE INDEX "business_orders_quotation_id_key" ON "business_orders"("quotation_id");

-- CreateIndex
CREATE UNIQUE INDEX "business_orders_purchase_request_id_key" ON "business_orders"("purchase_request_id");

-- CreateIndex
CREATE INDEX "business_orders_kind_created_at_idx" ON "business_orders"("kind", "created_at");

-- CreateIndex
CREATE INDEX "business_orders_customer_id_created_at_idx" ON "business_orders"("customer_id", "created_at");

-- CreateIndex
CREATE INDEX "business_orders_supplier_id_created_at_idx" ON "business_orders"("supplier_id", "created_at");

-- CreateIndex
CREATE INDEX "business_orders_warehouse_id_current_step_idx" ON "business_orders"("warehouse_id", "current_step");

-- CreateIndex
CREATE INDEX "business_orders_seller_user_id_idx" ON "business_orders"("seller_user_id");

-- CreateIndex
CREATE INDEX "order_lines_product_id_order_id_idx" ON "order_lines"("product_id", "order_id");

-- CreateIndex
CREATE UNIQUE INDEX "order_lines_order_id_line_no_key" ON "order_lines"("order_id", "line_no");

-- CreateIndex
CREATE INDEX "order_step_events_completed_by_user_id_completed_at_idx" ON "order_step_events"("completed_by_user_id", "completed_at");

-- CreateIndex
CREATE UNIQUE INDEX "order_step_events_order_id_step_no_key" ON "order_step_events"("order_id", "step_no");

-- CreateIndex
CREATE UNIQUE INDEX "dispatches_order_id_key" ON "dispatches"("order_id");

-- CreateIndex
CREATE UNIQUE INDEX "dispatches_dispatch_number_key" ON "dispatches"("dispatch_number");

-- CreateIndex
CREATE INDEX "dispatches_warehouse_id_dispatched_at_idx" ON "dispatches"("warehouse_id", "dispatched_at");

-- CreateIndex
CREATE INDEX "dispatches_carrier_supplier_id_idx" ON "dispatches"("carrier_supplier_id");

-- CreateIndex
CREATE UNIQUE INDEX "goods_receipts_order_id_key" ON "goods_receipts"("order_id");

-- CreateIndex
CREATE UNIQUE INDEX "goods_receipts_receipt_number_key" ON "goods_receipts"("receipt_number");

-- CreateIndex
CREATE INDEX "goods_receipts_warehouse_id_received_at_idx" ON "goods_receipts"("warehouse_id", "received_at");

-- CreateIndex
CREATE INDEX "goods_receipts_received_by_user_id_idx" ON "goods_receipts"("received_by_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "sales_invoices_order_id_key" ON "sales_invoices"("order_id");

-- CreateIndex
CREATE INDEX "sales_invoices_customer_id_due_at_idx" ON "sales_invoices"("customer_id", "due_at");

-- CreateIndex
CREATE INDEX "sales_invoices_tax_status_issued_at_idx" ON "sales_invoices"("tax_status", "issued_at");

-- CreateIndex
CREATE INDEX "sales_invoices_original_invoice_id_idx" ON "sales_invoices"("original_invoice_id");

-- CreateIndex
CREATE UNIQUE INDEX "sales_invoices_series_number_key" ON "sales_invoices"("series", "number");

-- CreateIndex
CREATE UNIQUE INDEX "supplier_invoices_order_id_key" ON "supplier_invoices"("order_id");

-- CreateIndex
CREATE INDEX "supplier_invoices_supplier_id_due_at_idx" ON "supplier_invoices"("supplier_id", "due_at");

-- CreateIndex
CREATE INDEX "supplier_invoices_created_by_user_id_idx" ON "supplier_invoices"("created_by_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "supplier_invoices_supplier_id_series_number_key" ON "supplier_invoices"("supplier_id", "series_number");

-- CreateIndex
CREATE UNIQUE INDEX "inventory_transfers_code_key" ON "inventory_transfers"("code");

-- CreateIndex
CREATE INDEX "inventory_transfers_status_created_at_idx" ON "inventory_transfers"("status", "created_at");

-- CreateIndex
CREATE INDEX "inventory_transfers_source_warehouse_id_created_at_idx" ON "inventory_transfers"("source_warehouse_id", "created_at");

-- CreateIndex
CREATE INDEX "inventory_transfers_destination_warehouse_id_created_at_idx" ON "inventory_transfers"("destination_warehouse_id", "created_at");

-- CreateIndex
CREATE INDEX "inventory_transfer_lines_product_id_idx" ON "inventory_transfer_lines"("product_id");

-- CreateIndex
CREATE UNIQUE INDEX "inventory_transfer_lines_transfer_id_line_no_key" ON "inventory_transfer_lines"("transfer_id", "line_no");

-- CreateIndex
CREATE UNIQUE INDEX "inventory_adjustments_code_key" ON "inventory_adjustments"("code");

-- CreateIndex
CREATE INDEX "inventory_adjustments_product_id_warehouse_id_created_at_idx" ON "inventory_adjustments"("product_id", "warehouse_id", "created_at");

-- CreateIndex
CREATE INDEX "inventory_adjustments_created_by_user_id_idx" ON "inventory_adjustments"("created_by_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "inventory_movements_adjustment_id_key" ON "inventory_movements"("adjustment_id");

-- CreateIndex
CREATE INDEX "inventory_movements_product_id_warehouse_id_occurred_at_id_idx" ON "inventory_movements"("product_id", "warehouse_id", "occurred_at", "id");

-- CreateIndex
CREATE INDEX "inventory_movements_warehouse_id_occurred_at_idx" ON "inventory_movements"("warehouse_id", "occurred_at");

-- CreateIndex
CREATE INDEX "inventory_movements_order_line_id_idx" ON "inventory_movements"("order_line_id");

-- CreateIndex
CREATE INDEX "inventory_movements_dispatch_id_idx" ON "inventory_movements"("dispatch_id");

-- CreateIndex
CREATE INDEX "inventory_movements_goods_receipt_id_idx" ON "inventory_movements"("goods_receipt_id");

-- CreateIndex
CREATE INDEX "inventory_movements_transfer_line_id_idx" ON "inventory_movements"("transfer_line_id");

-- CreateIndex
CREATE INDEX "inventory_movements_created_by_user_id_idx" ON "inventory_movements"("created_by_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "inventory_movements_transfer_line_id_movement_leg_key" ON "inventory_movements"("transfer_line_id", "movement_leg");

-- CreateIndex
CREATE UNIQUE INDEX "bank_accounts_label_key" ON "bank_accounts"("label");

-- CreateIndex
CREATE INDEX "bank_accounts_is_active_idx" ON "bank_accounts"("is_active");

-- CreateIndex
CREATE UNIQUE INDEX "treasury_movements_code_key" ON "treasury_movements"("code");

-- CreateIndex
CREATE INDEX "treasury_movements_occurred_at_channel_idx" ON "treasury_movements"("occurred_at", "channel");

-- CreateIndex
CREATE INDEX "treasury_movements_bank_account_id_occurred_at_idx" ON "treasury_movements"("bank_account_id", "occurred_at");

-- CreateIndex
CREATE INDEX "treasury_movements_sales_invoice_id_occurred_at_idx" ON "treasury_movements"("sales_invoice_id", "occurred_at");

-- CreateIndex
CREATE INDEX "treasury_movements_supplier_invoice_id_occurred_at_idx" ON "treasury_movements"("supplier_invoice_id", "occurred_at");

-- CreateIndex
CREATE INDEX "treasury_movements_created_by_user_id_idx" ON "treasury_movements"("created_by_user_id");

-- CreateIndex
CREATE INDEX "company_settings_default_warehouse_id_idx" ON "company_settings"("default_warehouse_id");

-- CreateIndex
CREATE UNIQUE INDEX "documents_storage_key_key" ON "documents"("storage_key");

-- CreateIndex
CREATE INDEX "documents_category_created_at_idx" ON "documents"("category", "created_at");

-- CreateIndex
CREATE INDEX "documents_related_order_id_idx" ON "documents"("related_order_id");

-- CreateIndex
CREATE INDEX "documents_related_customer_id_idx" ON "documents"("related_customer_id");

-- CreateIndex
CREATE INDEX "documents_related_supplier_id_idx" ON "documents"("related_supplier_id");

-- CreateIndex
CREATE INDEX "documents_uploaded_by_user_id_idx" ON "documents"("uploaded_by_user_id");

-- CreateIndex
CREATE INDEX "audit_events_occurred_at_idx" ON "audit_events"("occurred_at" DESC);

-- CreateIndex
CREATE INDEX "audit_events_user_id_occurred_at_idx" ON "audit_events"("user_id", "occurred_at" DESC);

-- CreateIndex
CREATE INDEX "audit_events_module_key_occurred_at_idx" ON "audit_events"("module_key", "occurred_at" DESC);

-- CreateIndex
CREATE INDEX "audit_events_entity_type_entity_id_idx" ON "audit_events"("entity_type", "entity_id");

-- CreateIndex
CREATE INDEX "audit_events_request_id_idx" ON "audit_events"("request_id");

-- CreateIndex
CREATE INDEX "report_schedules_is_enabled_frequency_idx" ON "report_schedules"("is_enabled", "frequency");

-- CreateIndex
CREATE INDEX "report_schedules_created_by_user_id_idx" ON "report_schedules"("created_by_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "report_schedules_report_key_key" ON "report_schedules"("report_key");

-- CreateIndex
CREATE INDEX "document_sequences_document_type_fiscal_year_idx" ON "document_sequences"("document_type", "fiscal_year");

-- AddForeignKey
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "permissions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_sessions" ADD CONSTRAINT "auth_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "customers" ADD CONSTRAINT "customers_salesperson_user_id_fkey" FOREIGN KEY ("salesperson_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "product_categories" ADD CONSTRAINT "product_categories_parent_category_id_fkey" FOREIGN KEY ("parent_category_id") REFERENCES "product_categories"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "products" ADD CONSTRAINT "products_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "product_categories"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "products" ADD CONSTRAINT "products_primary_supplier_id_fkey" FOREIGN KEY ("primary_supplier_id") REFERENCES "suppliers"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "warehouses" ADD CONSTRAINT "warehouses_manager_user_id_fkey" FOREIGN KEY ("manager_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "drivers" ADD CONSTRAINT "drivers_carrier_supplier_id_fkey" FOREIGN KEY ("carrier_supplier_id") REFERENCES "suppliers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "vehicles" ADD CONSTRAINT "vehicles_carrier_supplier_id_fkey" FOREIGN KEY ("carrier_supplier_id") REFERENCES "suppliers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "vehicles" ADD CONSTRAINT "vehicles_default_driver_id_fkey" FOREIGN KEY ("default_driver_id") REFERENCES "drivers"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotations" ADD CONSTRAINT "quotations_customer_id_fkey" FOREIGN KEY ("customer_id") REFERENCES "customers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotations" ADD CONSTRAINT "quotations_seller_user_id_fkey" FOREIGN KEY ("seller_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotations" ADD CONSTRAINT "quotations_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotation_lines" ADD CONSTRAINT "quotation_lines_quotation_id_fkey" FOREIGN KEY ("quotation_id") REFERENCES "quotations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "quotation_lines" ADD CONSTRAINT "quotation_lines_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_requests" ADD CONSTRAINT "purchase_requests_requested_by_user_id_fkey" FOREIGN KEY ("requested_by_user_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_requests" ADD CONSTRAINT "purchase_requests_reviewed_by_user_id_fkey" FOREIGN KEY ("reviewed_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_requests" ADD CONSTRAINT "purchase_requests_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_requests" ADD CONSTRAINT "purchase_requests_suggested_supplier_id_fkey" FOREIGN KEY ("suggested_supplier_id") REFERENCES "suppliers"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_request_lines" ADD CONSTRAINT "purchase_request_lines_purchase_request_id_fkey" FOREIGN KEY ("purchase_request_id") REFERENCES "purchase_requests"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "purchase_request_lines" ADD CONSTRAINT "purchase_request_lines_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_customer_id_fkey" FOREIGN KEY ("customer_id") REFERENCES "customers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_supplier_id_fkey" FOREIGN KEY ("supplier_id") REFERENCES "suppliers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_quotation_id_fkey" FOREIGN KEY ("quotation_id") REFERENCES "quotations"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_purchase_request_id_fkey" FOREIGN KEY ("purchase_request_id") REFERENCES "purchase_requests"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_seller_user_id_fkey" FOREIGN KEY ("seller_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "business_orders" ADD CONSTRAINT "business_orders_cancelled_by_user_id_fkey" FOREIGN KEY ("cancelled_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "order_lines" ADD CONSTRAINT "order_lines_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "business_orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "order_lines" ADD CONSTRAINT "order_lines_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "order_step_events" ADD CONSTRAINT "order_step_events_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "business_orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "order_step_events" ADD CONSTRAINT "order_step_events_completed_by_user_id_fkey" FOREIGN KEY ("completed_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dispatches" ADD CONSTRAINT "dispatches_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "business_orders"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dispatches" ADD CONSTRAINT "dispatches_carrier_supplier_id_fkey" FOREIGN KEY ("carrier_supplier_id") REFERENCES "suppliers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dispatches" ADD CONSTRAINT "dispatches_vehicle_id_fkey" FOREIGN KEY ("vehicle_id") REFERENCES "vehicles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dispatches" ADD CONSTRAINT "dispatches_driver_id_fkey" FOREIGN KEY ("driver_id") REFERENCES "drivers"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dispatches" ADD CONSTRAINT "dispatches_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dispatches" ADD CONSTRAINT "dispatches_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "goods_receipts" ADD CONSTRAINT "goods_receipts_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "business_orders"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "goods_receipts" ADD CONSTRAINT "goods_receipts_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "goods_receipts" ADD CONSTRAINT "goods_receipts_received_by_user_id_fkey" FOREIGN KEY ("received_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_invoices" ADD CONSTRAINT "sales_invoices_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "business_orders"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_invoices" ADD CONSTRAINT "sales_invoices_customer_id_fkey" FOREIGN KEY ("customer_id") REFERENCES "customers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_invoices" ADD CONSTRAINT "sales_invoices_original_invoice_id_fkey" FOREIGN KEY ("original_invoice_id") REFERENCES "sales_invoices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_invoices" ADD CONSTRAINT "supplier_invoices_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "business_orders"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_invoices" ADD CONSTRAINT "supplier_invoices_supplier_id_fkey" FOREIGN KEY ("supplier_id") REFERENCES "suppliers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "supplier_invoices" ADD CONSTRAINT "supplier_invoices_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_transfers" ADD CONSTRAINT "inventory_transfers_source_warehouse_id_fkey" FOREIGN KEY ("source_warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_transfers" ADD CONSTRAINT "inventory_transfers_destination_warehouse_id_fkey" FOREIGN KEY ("destination_warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_transfers" ADD CONSTRAINT "inventory_transfers_responsible_user_id_fkey" FOREIGN KEY ("responsible_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_transfer_lines" ADD CONSTRAINT "inventory_transfer_lines_transfer_id_fkey" FOREIGN KEY ("transfer_id") REFERENCES "inventory_transfers"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_transfer_lines" ADD CONSTRAINT "inventory_transfer_lines_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_adjustments" ADD CONSTRAINT "inventory_adjustments_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_adjustments" ADD CONSTRAINT "inventory_adjustments_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_adjustments" ADD CONSTRAINT "inventory_adjustments_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_order_line_id_fkey" FOREIGN KEY ("order_line_id") REFERENCES "order_lines"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_dispatch_id_fkey" FOREIGN KEY ("dispatch_id") REFERENCES "dispatches"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_goods_receipt_id_fkey" FOREIGN KEY ("goods_receipt_id") REFERENCES "goods_receipts"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_transfer_line_id_fkey" FOREIGN KEY ("transfer_line_id") REFERENCES "inventory_transfer_lines"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_adjustment_id_fkey" FOREIGN KEY ("adjustment_id") REFERENCES "inventory_adjustments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "treasury_movements" ADD CONSTRAINT "treasury_movements_bank_account_id_fkey" FOREIGN KEY ("bank_account_id") REFERENCES "bank_accounts"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "treasury_movements" ADD CONSTRAINT "treasury_movements_sales_invoice_id_fkey" FOREIGN KEY ("sales_invoice_id") REFERENCES "sales_invoices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "treasury_movements" ADD CONSTRAINT "treasury_movements_supplier_invoice_id_fkey" FOREIGN KEY ("supplier_invoice_id") REFERENCES "supplier_invoices"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "treasury_movements" ADD CONSTRAINT "treasury_movements_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "company_settings" ADD CONSTRAINT "company_settings_default_warehouse_id_fkey" FOREIGN KEY ("default_warehouse_id") REFERENCES "warehouses"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "documents" ADD CONSTRAINT "documents_related_order_id_fkey" FOREIGN KEY ("related_order_id") REFERENCES "business_orders"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "documents" ADD CONSTRAINT "documents_related_customer_id_fkey" FOREIGN KEY ("related_customer_id") REFERENCES "customers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "documents" ADD CONSTRAINT "documents_related_supplier_id_fkey" FOREIGN KEY ("related_supplier_id") REFERENCES "suppliers"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "documents" ADD CONSTRAINT "documents_uploaded_by_user_id_fkey" FOREIGN KEY ("uploaded_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "audit_events" ADD CONSTRAINT "audit_events_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "audit_events" ADD CONSTRAINT "audit_events_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "report_schedules" ADD CONSTRAINT "report_schedules_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
