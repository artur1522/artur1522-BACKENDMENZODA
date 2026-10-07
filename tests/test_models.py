"""Paridad del modelo SQLAlchemy contra el DDL exacto generado por Prisma.

El fixture `tests/fixtures/prisma-ref.sql` se obtuvo con:
    npx prisma migrate diff --from-empty --to-schema-datamodel backend/prisma/schema.prisma --script
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import sqlalchemy as sa
from app.db.base import Base
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex

REF_SQL = (Path(__file__).parent / "fixtures" / "prisma-ref.sql").read_text(encoding="utf-8")

EXPECTED_TABLES = {
    "audit_events",
    "auth_sessions",
    "bank_accounts",
    "business_orders",
    "company_settings",
    "customers",
    "dispatches",
    "document_sequences",
    "documents",
    "drivers",
    "goods_receipts",
    "inventory_adjustments",
    "inventory_movements",
    "inventory_transfer_lines",
    "inventory_transfers",
    "order_lines",
    "order_step_events",
    "permissions",
    "product_categories",
    "products",
    "purchase_request_lines",
    "purchase_requests",
    "quotation_lines",
    "quotations",
    "report_schedules",
    "role_permissions",
    "roles",
    "sales_invoices",
    "supplier_invoices",
    "suppliers",
    "treasury_movements",
    "users",
    "vehicles",
    "warehouses",
}


def _norm_type(sql_type: str) -> str:
    t = sql_type.replace('"', "").upper()
    t = re.sub(r"\s+", "", t)
    t = t.replace("NUMERIC(", "DECIMAL(")
    t = re.sub(r"TIMESTAMP\((\d+)\)WITHTIMEZONE", r"TIMESTAMPTZ(\1)", t)
    return t.replace("TIMESTAMPWITHTIMEZONE", "TIMESTAMPTZ")


def _norm_index_cols(cols: str) -> tuple[str, ...]:
    return tuple(re.sub(r"\s+", " ", part.replace('"', "").strip()) for part in cols.split(","))


def parse_ref_enums(sql: str) -> dict[str, tuple[str, ...]]:
    return {
        m.group(1): tuple(re.findall(r"'([^']*)'", m.group(2)))
        for m in re.finditer(r'CREATE TYPE "([^"]+)" AS ENUM \(([^)]*)\);', sql)
    }


def parse_ref_tables(sql: str) -> dict[str, dict]:
    tables: dict[str, dict] = {}
    for m in re.finditer(r'CREATE TABLE "([^"]+)" \((.*?)\);\n', sql, re.S):
        name, body = m.group(1), m.group(2)
        columns: dict[str, tuple[str, bool, str | None]] = {}
        pk: tuple[str, ...] = ()
        for raw in body.split("\n"):
            line = raw.strip().rstrip(",")
            if not line:
                continue
            if line.startswith("CONSTRAINT") and "PRIMARY KEY" in line:
                pk = tuple(re.findall(r'"([^"]+)"', line.split("PRIMARY KEY", 1)[1]))
                continue
            cm = re.match(r'"([^"]+)" (.*)$', line)
            assert cm, f"línea de columna inesperada: {line!r}"
            col_name, rest = cm.group(1), cm.group(2)
            nullable, default = True, None
            nn = re.match(r"^(.*?) NOT NULL(?: DEFAULT (.*))?$", rest)
            if nn:
                col_type, default, nullable = nn.group(1), nn.group(2), False
            else:
                dm = re.match(r"^(.*?) DEFAULT (.*)$", rest)
                col_type, default = (dm.group(1), dm.group(2)) if dm else (rest, None)
            columns[col_name] = (_norm_type(col_type), nullable, default)
        tables[name] = {"columns": columns, "pk": pk}
    return tables


def parse_ref_indexes(sql: str) -> dict[str, tuple[str, tuple[str, ...], bool]]:
    out: dict[str, tuple[str, tuple[str, ...], bool]] = {}
    for m in re.finditer(r'CREATE (UNIQUE )?INDEX "([^"]+)" ON "([^"]+)"\s*\(([^)]*)\);', sql):
        out[m.group(2)] = (
            m.group(3),
            _norm_index_cols(m.group(4)),
            bool(m.group(1)),
        )
    return out


def parse_ref_fks(sql: str) -> dict[str, tuple]:
    pat = re.compile(
        r'ALTER TABLE "([^"]+)" ADD CONSTRAINT "([^"]+)" FOREIGN KEY \(([^)]*)\)'
        r'\s*REFERENCES "([^"]+)"\(([^)]*)\)'
        r"\s*ON DELETE (RESTRICT|CASCADE|SET NULL|SET DEFAULT|NO ACTION)"
        r"\s*ON UPDATE (CASCADE|RESTRICT|SET NULL|SET DEFAULT|NO ACTION);"
    )
    return {
        m.group(2): (
            m.group(1),
            _norm_index_cols(m.group(3)),
            m.group(4),
            _norm_index_cols(m.group(5)),
            m.group(6),
            m.group(7),
        )
        for m in pat.finditer(sql)
    }


@pytest.fixture(scope="session")
def ref() -> dict:
    return {
        "enums": parse_ref_enums(REF_SQL),
        "tables": parse_ref_tables(REF_SQL),
        "indexes": parse_ref_indexes(REF_SQL),
        "fks": parse_ref_fks(REF_SQL),
    }


@pytest.fixture(scope="session")
def our() -> dict:
    import app.models  # noqa: F401
    from sqlalchemy.orm import configure_mappers

    configure_mappers()

    columns: dict[str, dict[str, tuple[str, bool, str | None]]] = {}
    pks: dict[str, tuple[str, ...]] = {}
    indexes: dict[str, tuple[str, tuple[str, ...], bool]] = {}
    fks: dict[str, tuple] = {}
    enums: dict[str, tuple[str, ...]] = {}

    for table in Base.metadata.sorted_tables:
        cols: dict[str, tuple[str, bool, str | None]] = {}
        for col in table.columns:
            default = None
            if col.server_default is not None:
                default = getattr(col.server_default, "text", None)
                if default is None:
                    default = str(col.server_default.arg)
            cols[col.name] = (
                _norm_type(str(col.type.compile(dialect=postgresql.dialect()))),
                col.nullable,
                default,
            )
            if isinstance(col.type, sa.Enum) and col.type.name and col.type.enum_class:
                values = tuple(member.value for member in col.type.enum_class)
                prev = enums.setdefault(col.type.name, values)
                assert prev == values, f"enum {col.type.name} inconsistente"
        columns[table.name] = cols
        pks[table.name] = tuple(c.name for c in table.primary_key)

        for idx in table.indexes:
            ddl = str(CreateIndex(idx).compile(dialect=postgresql.dialect()))
            ddl = ddl.replace('"', "")
            m = re.match(r"CREATE (UNIQUE )?INDEX (\S+) ON (\S+)\s*\(([^)]*)\)", ddl)
            assert m, f"DDL de índice ilegible: {ddl}"
            indexes[m.group(2)] = (
                m.group(3),
                _norm_index_cols(m.group(4)),
                bool(m.group(1)),
            )

        for fk in table.foreign_key_constraints:
            assert fk.name, f"FK sin nombre en {table.name}"
            local = tuple(e.parent.name for e in fk.elements)
            remote = tuple(e.column.name for e in fk.elements)
            fks[fk.name] = (
                table.name,
                local,
                fk.elements[0].column.table.name,
                remote,
                fk.ondelete,
                fk.onupdate,
            )

    return {
        "enums": enums,
        "tables": columns,
        "pks": pks,
        "indexes": indexes,
        "fks": fks,
    }


def _report(label: str, missing: set, extra: set, changed: dict) -> str:
    lines = [f"[{label}]"]
    if missing:
        lines.append(f"  faltan en el modelo: {sorted(missing)}")
    if extra:
        lines.append(f"  sobran en el modelo: {sorted(extra)}")
    for key, (ours, theirs) in sorted(changed.items()):
        lines.append(f"  distinto {key}:")
        lines.append(f"    modelo: {ours}")
        lines.append(f"    prisma: {theirs}")
    return "\n".join(lines)


def _compare(label: str, ours: dict, theirs: dict) -> None:
    missing = set(theirs) - set(ours)
    extra = set(ours) - set(theirs)
    changed = {k: (ours[k], theirs[k]) for k in set(ours) & set(theirs) if ours[k] != theirs[k]}
    assert not (missing or extra or changed), _report(label, missing, extra, changed)


def test_table_names_match(ref: dict, our: dict) -> None:
    missing = set(ref["tables"]) - set(our["tables"])
    extra = set(our["tables"]) - set(ref["tables"])
    assert not (missing or extra), f"faltan={sorted(missing)} sobran={sorted(extra)}"
    assert set(our["tables"]) == EXPECTED_TABLES
    assert len(our["tables"]) == 34


def test_enum_types_match(ref: dict, our: dict) -> None:
    assert len(ref["enums"]) == 27
    _compare("enums", our["enums"], ref["enums"])


def test_columns_match(ref: dict, our: dict) -> None:
    for table, expected in ref["tables"].items():
        _compare(
            f"columnas de {table}",
            our["tables"][table],
            expected["columns"],
        )


def test_primary_keys_match(ref: dict, our: dict) -> None:
    for table, expected in ref["tables"].items():
        assert our["pks"][table] == expected["pk"], (
            f"PK de {table}: modelo={our['pks'][table]} prisma={expected['pk']}"
        )


def test_indexes_match(ref: dict, our: dict) -> None:
    assert len(ref["indexes"]) == len(our["indexes"]) == len(set(ref["indexes"]))
    _compare("índices", our["indexes"], ref["indexes"])


def test_foreign_keys_match(ref: dict, our: dict) -> None:
    assert len(ref["fks"]) == 78
    _compare("FKs", our["fks"], ref["fks"])


def test_no_unnamed_indexes_or_constraints() -> None:
    from sqlalchemy.orm import configure_mappers

    configure_mappers()
    for table in Base.metadata.sorted_tables:
        for idx in table.indexes:
            assert idx.name, f"índice sin nombre en {table.name}"
        for constraint in table.constraints:
            if isinstance(constraint, (sa.PrimaryKeyConstraint,)):
                assert constraint.name == f"{table.name}_pkey"
