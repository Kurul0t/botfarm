from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String,Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class IncubatorState(str, Enum):
    AVAILABLE = "available"
    INCUBATING = "incubating"
    BROKEN = "broken"


class Incubator(Base):
    __tablename__ = "incubators"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    number: Mapped[int] = mapped_column(nullable=False)

    eggs_amount: Mapped[int | None] = mapped_column(
        nullable=True
    )

    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String(20),
        default=IncubatorState.AVAILABLE.value,

    )
    
class Instruction(Base):
    __tablename__ = "instructions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(default='Інструкція',nullable=True)
    script: Mapped[str] = mapped_column(Text)
