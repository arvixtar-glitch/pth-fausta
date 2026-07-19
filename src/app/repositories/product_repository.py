"""Atomic persistence for the product aggregate and its dictionaries."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductBarcode, ProductCategory, UnitOfMeasure
from app.persistence.session_factory import SessionFactory
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Persist products, categories, units, and barcodes."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _query():
        return select(Product).options(
            selectinload(Product.category),
            selectinload(Product.unit),
            selectinload(Product.barcodes),
        )

    def get(self, product_id: int) -> Product | None:
        with self._session_factory.session() as session:
            return session.scalar(self._query().where(Product.id == product_id))

    def list_all(self) -> list[Product]:
        with self._session_factory.session() as session:
            return list(
                session.scalars(self._query().order_by(Product.name, Product.id))
            )

    def save(
        self,
        product_id: int | None,
        values: dict[str, Any],
        barcodes: Iterable[dict[str, Any]],
    ) -> Product:
        with self._session_factory.session() as session:
            try:
                product = (
                    Product()
                    if product_id is None
                    else session.get(Product, product_id)
                )
                if product is None:
                    raise LookupError("Prekė ar paslauga nerasta.")
                if product_id is None:
                    session.add(product)
                for field, value in values.items():
                    setattr(product, field, value)
                if product_id is not None:
                    product.barcodes.clear()
                    session.flush()
                product.barcodes = [ProductBarcode(**item) for item in barcodes]
                session.commit()
                product_id = product.id
            except Exception:
                session.rollback()
                raise
        result = self.get(product_id)
        if result is None:
            raise LookupError("Prekė ar paslauga nerasta.")
        return result

    def set_status(self, product_id: int, status: str) -> Product:
        with self._session_factory.session() as session:
            product = session.get(Product, product_id)
            if product is None:
                raise LookupError("Prekė ar paslauga nerasta.")
            product.status = status
            session.commit()
        result = self.get(product_id)
        if result is None:
            raise LookupError("Prekė ar paslauga nerasta.")
        return result

    def list_categories(self) -> list[ProductCategory]:
        with self._session_factory.session() as session:
            return list(
                session.scalars(select(ProductCategory).order_by(ProductCategory.name))
            )

    def create_category(self, name: str, normalized_name: str) -> ProductCategory:
        with self._session_factory.session() as session:
            category = ProductCategory(name=name, normalized_name=normalized_name)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category

    def list_units(self) -> list[UnitOfMeasure]:
        with self._session_factory.session() as session:
            return list(
                session.scalars(select(UnitOfMeasure).order_by(UnitOfMeasure.id))
            )

    def create_unit(self, code: str, name: str) -> UnitOfMeasure:
        with self._session_factory.session() as session:
            unit = UnitOfMeasure(code=code, name=name)
            session.add(unit)
            session.commit()
            session.refresh(unit)
            return unit
