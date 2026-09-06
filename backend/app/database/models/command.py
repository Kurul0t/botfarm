from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from database.base import Base



class Command(Base):
    __tablename__ = "commands"

    id: Mapped[int] = mapped_column(primary_key=True)
    function_name: Mapped[str] = mapped_column(nullable=False)
    arguments: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    counter: Mapped[int] = mapped_column(default=1)