from sqlalchemy import Integer, String, Numeric, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from decimal import Decimal

from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    firstname: Mapped[str] = mapped_column(String)
    lastname: Mapped[str] = mapped_column(String)
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), default=Decimal('0.00'))
    total_income: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), default=Decimal('0.00'))
    total_expense: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), default=Decimal('0.00'))
    savings: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), default=Decimal('0.00'))
    goal: Mapped[Decimal | None] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    type: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
