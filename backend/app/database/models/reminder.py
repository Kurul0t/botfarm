from database.base import Base
from sqlalchemy import Text,BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime



class Reminder(Base):
    __tablename__ = "reminders"
    id: Mapped[int] = mapped_column(primary_key=True)
    datetime: Mapped[datetime]
    user_id: Mapped[int]=mapped_column(BigInteger,nullable=False,)
    bot_id: Mapped[int] = mapped_column(BigInteger,nullable=False,)
    text: Mapped[str] = mapped_column(Text,nullable=False,) 