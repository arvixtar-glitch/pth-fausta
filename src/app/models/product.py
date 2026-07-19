"""Product aggregate ORM models and domain constants."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.company import utc_now
from app.persistence.orm import OrmBase

PRODUCT_TYPE_PRODUCT = "product"
PRODUCT_TYPE_SERVICE = "service"
PRODUCT_STATUS_ACTIVE = "active"
PRODUCT_STATUS_INACTIVE = "inactive"
PRICE_BASIS_NET = "net"
PRICE_BASIS_FINAL = "final"
VAT_TREATMENT_RATE = "rate"
VAT_TREATMENT_NOT_OBJECT = "not_vat_object"
VAT_TREATMENT_NOT_APPLICABLE = "not_applicable"


class ProductCategory(OrmBase):
    """Represent a normalized product category."""

    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    normalized_name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class UnitOfMeasure(OrmBase):
    """Represent a controlled unit-of-measure dictionary entry."""

    __tablename__ = "units_of_measure"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default=PRODUCT_STATUS_ACTIVE)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class Product(OrmBase):
    """Represent a product or service and its pricing state."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    product_type: Mapped[str] = mapped_column(String(20), index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_categories.id"), index=True
    )
    unit_id: Mapped[int] = mapped_column(ForeignKey("units_of_measure.id"), index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    price_basis: Mapped[str] = mapped_column(String(20))
    vat_treatment: Mapped[str] = mapped_column(String(30))
    vat_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(
        String(20), default=PRODUCT_STATUS_ACTIVE, index=True
    )
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    category: Mapped[ProductCategory | None] = relationship()
    unit: Mapped[UnitOfMeasure] = relationship()
    barcodes: Mapped[list[ProductBarcode]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    @property
    def default_barcode(self) -> ProductBarcode | None:
        """Return the explicitly selected default or the first barcode."""
        return next((item for item in self.barcodes if item.is_default), None)


class ProductBarcode(OrmBase):
    """Represent a globally unique barcode belonging to a product."""

    __tablename__ = "product_barcodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    barcode: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    barcode_type: Mapped[str] = mapped_column(String(20), default="other")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    product: Mapped[Product] = relationship(back_populates="barcodes")
