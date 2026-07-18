"""Customer ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.company import utc_now
from app.persistence.orm import OrmBase

CUSTOMER_TYPE_COMPANY = "company"
CUSTOMER_TYPE_INDIVIDUAL = "individual"
CUSTOMER_STATUS_ACTIVE = "active"
CUSTOMER_STATUS_INACTIVE = "inactive"


class Customer(OrmBase):
    """Represent a legal or individual customer."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_type: Mapped[str] = mapped_column(
        String(20), default=CUSTOMER_TYPE_COMPANY, index=True
    )
    name: Mapped[str] = mapped_column(String(200), index=True)
    company_code: Mapped[str] = mapped_column(String(50), default="", index=True)
    vat_code: Mapped[str] = mapped_column(String(50), default="", index=True)
    address: Mapped[str] = mapped_column(String(250), default="")
    city: Mapped[str] = mapped_column(String(100), default="", index=True)
    postal_code: Mapped[str] = mapped_column(String(20), default="")
    country_code: Mapped[str] = mapped_column(String(100), default="Lietuva")
    phone: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(20), default=CUSTOMER_STATUS_ACTIVE, index=True
    )
    search_text: Mapped[str] = mapped_column(Text, default="", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
