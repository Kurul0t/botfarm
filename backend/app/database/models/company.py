from sqlalchemy import ForeignKey,BigInteger,Text
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from typing import Optional


from database.base import Base


class EmployeeState(str, Enum):
    OWNER = "власник"


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    company_login: Mapped[str]= mapped_column(unique=True)
    owner_password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id")
    )
    user_id: Mapped[int]= mapped_column(BigInteger,unique=True)

    role: Mapped[str] = mapped_column(default=EmployeeState.OWNER)
    
    first_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    login: Mapped[Optional[str]] = mapped_column(nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(nullable=True)

    

class GoogleSheet(Base):
    __tablename__ = "google_sheets"
    id: Mapped[int] = mapped_column( primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    key: Mapped[str] = mapped_column(Text)