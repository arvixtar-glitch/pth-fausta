"""Company profile ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.orm import OrmBase


def utc_now() -> datetime:
    """Return the current timezone-aware UTC time."""
    return datetime.now(timezone.utc)


class Company(OrmBase):
    """Represent the single application company profile."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    company_code: Mapped[str] = mapped_column(String(50), default="")
    vat_code: Mapped[str] = mapped_column(String(50), default="")
    address: Mapped[str] = mapped_column(String(250), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    postal_code: Mapped[str] = mapped_column(String(20), default="")
    country_code: Mapped[str] = mapped_column(String(2), default="LT")
    phone: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    website: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    bank_accounts: Mapped[list[CompanyBankAccount]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class CompanyBankAccount(OrmBase):
    """Represent a bank account owned by the company."""

    __tablename__ = "company_bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    bank_name: Mapped[str] = mapped_column(String(200))
    swift_bic: Mapped[str] = mapped_column(String(20), default="")
    iban: Mapped[str] = mapped_column(String(50))
    account_holder: Mapped[str] = mapped_column(String(200), default="")
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    company: Mapped[Company] = relationship(back_populates="bank_accounts")
