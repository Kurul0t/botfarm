from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey,BigInteger

from database.base import Base

class TelegramBot(Base):
    __tablename__ = "telegram_bots"
    id: Mapped[int] = mapped_column(primary_key = True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    tg_bot_id: Mapped[int]= mapped_column(BigInteger)
    token: Mapped[str]
    admin_password_hash: Mapped[str] = mapped_column(default="")
    is_active: Mapped[bool] = mapped_column(default=True)
