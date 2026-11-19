
"""Add incubator device identifiers, type and capacity.

Revision ID: abbb56c20df0
Revises: 672e7ff02fbe
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "abbb56c20df0"
down_revision: Union[str, Sequence[str], None] = "672e7ff02fbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def calculate_check_digit(value: str) -> str:
    """Luhn checksum for a numeric identifier."""
    total = 0

    for index, char in enumerate(reversed(value)):
        digit = int(char)

        if index % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9

        total += digit

    return str((-total) % 10)


def generate_device_id(
    company_id: int,
    device_id: int,
    category_code: int = 1,
) -> str:
    if not (0 <= company_id <= 999999):
        raise ValueError("Company ID exceeds 6 digits")

    if not (0 <= device_id <= 999999):
        raise ValueError("Device ID exceeds 6 digits")

    if not (0 <= category_code <= 99):
        raise ValueError("Category code exceeds 2 digits")

    company = f"{company_id:06d}"
    category = f"{category_code:02d}"
    device = f"{device_id:06d}"

    check_digit = calculate_check_digit(
        company + category + device
    )

    return f"{company}-{category}-{device}-{check_digit}"


def upgrade() -> None:
    # 1. Додаємо тип пристрою
    op.add_column(
        "incubators",
        sa.Column(
            "device_type",
            sa.String(length=20),
            nullable=False,
            server_default="manual",
        ),
    )

    # 2. Додаємо місткість
    op.add_column(
        "incubators",
        sa.Column(
            "capacity",
            sa.Integer(),
            nullable=True,
        ),
    )

    # 3. Додаємо ідентифікатор
    op.add_column(
        "incubators",
        sa.Column(
            "uuid",
            sa.String(length=32),
            nullable=True,
        ),
    )

    # 4. Отримуємо існуючі інкубатори
    connection = op.get_bind()

    incubators = connection.execute(
        sa.text(
            "SELECT id, company_id FROM incubators"
        )
    ).mappings().all()

    # 5. Генеруємо Smart Farm ID
    for incubator in incubators:
        device_code = generate_device_id(
            company_id=incubator["company_id"],
            device_id=incubator["id"],
            category_code=1,
        )

        connection.execute(
            sa.text(
                """
                UPDATE incubators
                SET uuid = :device_code
                WHERE id = :id
                """
            ),
            {
                "device_code": device_code,
                "id": incubator["id"],
            },
        )

    # 6. Робимо ідентифікатор обов'язковим
    op.alter_column(
        "incubators",
        "uuid",
        existing_type=sa.String(length=32),
        nullable=False,
    )

    # 7. Забезпечуємо унікальність
    op.create_unique_constraint(
        "uq_incubators_uuid",
        "incubators",
        ["uuid"],
    )

    # 8. Прибираємо тимчасовий default
    op.alter_column(
        "incubators",
        "device_type",
        existing_type=sa.String(length=20),
        server_default=None,
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_incubators_uuid",
        "incubators",
        type_="unique",
    )

    op.drop_column("incubators", "uuid")
    op.drop_column("incubators", "capacity")
    op.drop_column("incubators", "device_type")
