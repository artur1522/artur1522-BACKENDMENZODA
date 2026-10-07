"""Base declarativa de SQLAlchemy 2.x con convención de nombres a la par de Prisma."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Prisma nombra constraints así en PostgreSQL:
#   roles_pkey · users_role_id_fkey · users_email_key · users_role_id_status_idx
NAMING_CONVENTION = {
    "pk": "%(table_name)s_pkey",
    "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "ix": "%(table_name)s_%(column_0_N_name)s_idx",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
