
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
    Text,
    
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


# ==================================================
# ENUMS
# ==================================================

class IncubatorState(str, Enum):
    AVAILABLE = "available"
    INCUBATING = "incubating"
    BROKEN = "broken"


class IncubatorType(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


# ==================================================
# INCUBATOR MODEL
# ==================================================

class Incubator(Base):
    __tablename__ = "incubators"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    device_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    number: Mapped[int] = mapped_column(
        nullable=False,
    )

    device_type: Mapped[str] = mapped_column(
        String(20),
        default=IncubatorType.MANUAL.value,
        nullable=False,
    )

    capacity: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    eggs_amount: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String(20),
        default=IncubatorState.AVAILABLE.value,
        nullable=False,
    )

    instruction_id: Mapped[int | None] = mapped_column(
        ForeignKey("instructions.id"),
        nullable=True,
    )



class IncubationState(Base):
    __tablename__ = "incubation_states"

    id: Mapped[int] = mapped_column(primary_key=True)

    incubator_id: Mapped[int] = mapped_column(
        ForeignKey("incubators.id"),
        unique=True,
        nullable=False
    )

    parameters: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False
    )



# ==================================================
# INSTRUCTION MODEL
# ==================================================

class Instruction(Base):
    __tablename__ = "instructions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        default="Інструкція",
        nullable=True,
    )

    script: Mapped[str] = mapped_column(
        Text,
    )
