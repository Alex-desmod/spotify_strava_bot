from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    tg_id = mapped_column(BigInteger, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(25))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    access_token: Mapped[str] = mapped_column(String(), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(), nullable=True)

