
"""Synchronize database schema with current SQLAlchemy models.

Revision ID: f1a6a65f4334
Revises: 42734ae99626
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a6a65f4334"
down_revision: Union[str, Sequence[str], None] = "42734ae99626"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = {
    "companies": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("company_login", sa.String(), nullable=False),
        sa.Column("owner_password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    ],
    "employees": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="власник"),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("login", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=True),
    ],
    "google_sheets": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
    ],
    "telegram_bots": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("tg_bot_id", sa.BigInteger(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("admin_password_hash", sa.String(), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    ],
    "instructions": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("script", sa.Text(), nullable=False),
    ],
    "incubators": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_code", sa.String(20), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("device_type", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("eggs_amount", sa.Integer(), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state", sa.String(20), nullable=False, server_default="available"),
        sa.Column("instruction_id", sa.Integer(), nullable=True),
    ],
    "incubation_states": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incubator_id", sa.Integer(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
    ],
    "reminders": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("datetime", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("bot_id", sa.BigInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("command", sa.Text(), nullable=True),
    ],
    "commands": [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("function_name", sa.String(), nullable=False),
        sa.Column("arguments", sa.JSON(), nullable=True),
        sa.Column("counter", sa.Integer(), nullable=False, server_default="1"),
    ],
}


FOREIGN_KEYS = [
    ("employees", "company_id", "companies"),
    ("google_sheets", "company_id", "companies"),
    ("telegram_bots", "company_id", "companies"),
    ("instructions", "company_id", "companies"),
    ("incubators", "company_id", "companies"),
    ("incubators", "instruction_id", "instructions"),
    ("incubation_states", "incubator_id", "incubators"),
]

UNIQUE_COLUMNS = [
    ("companies", "company_login"),
    ("employees", "user_id"),
    ("incubators", "device_code"),
    ("incubation_states", "incubator_id"),
]


def _inspector():
    return sa.inspect(op.get_bind())


def _has_table(table_name: str) -> bool:
    return _inspector().has_table(table_name)


def _columns(table_name: str) -> set[str]:
    return {
        column["name"]
        for column in _inspector().get_columns(table_name)
    }


def _add_missing_columns(table_name: str, columns):
    existing = _columns(table_name)

    for column in columns:
        if column.name in existing:
            continue

        # PostgreSQL cannot add a NOT NULL column to a populated
        # table without providing values for existing records.
        if not column.nullable and column.server_default is None:
            raise RuntimeError(
                f"Cannot safely add {table_name}.{column.name}: "
                "a NOT NULL column requires a data backfill."
            )

        op.add_column(table_name, column.copy())
        existing.add(column.name)


def _ensure_foreign_keys():
    for table_name, column_name, target_table in FOREIGN_KEYS:
        constraints = _inspector().get_foreign_keys(table_name)

        exists = any(
            fk.get("constrained_columns") == [column_name]
            and fk.get("referred_table") == target_table
            and fk.get("referred_columns") == ["id"]
            for fk in constraints
        )

        if not exists:
            op.create_foreign_key(
                f"fk_{table_name}_{column_name}",
                table_name,
                target_table,
                [column_name],
                ["id"],
            )


def _ensure_unique_constraints():
    for table_name, column_name in UNIQUE_COLUMNS:
        inspector = _inspector()

        unique_constraints = inspector.get_unique_constraints(table_name)
        indexes = inspector.get_indexes(table_name)

        exists = any(
            set(item.get("column_names") or []) == {column_name}
            for item in unique_constraints
        ) or any(
            index.get("unique")
            and set(index.get("column_names") or []) == {column_name}
            for index in indexes
        )

        if not exists:
            op.create_unique_constraint(
                f"uq_{table_name}_{column_name}",
                table_name,
                [column_name],
            )


def upgrade() -> None:
    # Create tables in dependency order.
    table_order = [
        "companies",
        "employees",
        "google_sheets",
        "telegram_bots",
        "instructions",
        "incubators",
        "incubation_states",
        "reminders",
        "commands",
    ]

    for table_name in table_order:
        if not _has_table(table_name):
            op.create_table(
                table_name,
                *(column.copy() for column in TABLES[table_name]),
            )
        else:
            _add_missing_columns(table_name, TABLES[table_name])

    _ensure_foreign_keys()
    _ensure_unique_constraints()


def downgrade() -> None:
    raise NotImplementedError(
        "Automatic downgrade is disabled because this migration "
        "may modify existing production tables."
    )
