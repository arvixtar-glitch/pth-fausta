"""Persistence, service, and controller tests for the product aggregate."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.controllers.product_controller import ProductController
from app.models.company import Company
from app.models.customer import Customer
from app.models.product import (
    PRICE_BASIS_FINAL,
    PRICE_BASIS_NET,
    PRODUCT_STATUS_INACTIVE,
    PRODUCT_TYPE_PRODUCT,
    PRODUCT_TYPE_SERVICE,
    VAT_TREATMENT_NOT_APPLICABLE,
    VAT_TREATMENT_NOT_OBJECT,
    VAT_TREATMENT_RATE,
    Product,
)
from app.persistence.orm import OrmBase
from app.persistence.session_factory import SessionFactory
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService


class VatCompanyService:
    def __init__(self, vat_payer: bool) -> None:
        self.vat_payer = vat_payer

    def is_vat_payer(self) -> bool:
        return self.vat_payer


@pytest.fixture
def repository() -> ProductRepository:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    OrmBase.metadata.create_all(engine)
    return ProductRepository(SessionFactory(engine))


@pytest.fixture
def service(repository: ProductRepository) -> ProductService:
    result = ProductService(repository, VatCompanyService(True))  # type: ignore[arg-type]
    result.ensure_default_units()
    return result


def values(service: ProductService, **overrides: Any) -> dict[str, Any]:
    data = service.product_values(product_type=PRODUCT_TYPE_PRODUCT)
    data.update({"name": "Popierius", "code": "P-1", "unit_price": "3.20"})
    data.update(overrides)
    return data


def test_product_orm_contains_approved_columns() -> None:
    assert set(Product.__table__.columns.keys()) == {
        "id",
        "code",
        "name",
        "product_type",
        "category_id",
        "unit_id",
        "unit_price",
        "price_basis",
        "vat_treatment",
        "vat_rate",
        "status",
        "notes",
        "created_at",
        "updated_at",
    }


def test_create_all_adds_product_tables_without_damaging_existing_data() -> None:
    engine = create_engine("sqlite://")
    Company.__table__.create(engine)
    Customer.__table__.create(engine)
    with engine.begin() as connection:
        connection.execute(Company.__table__.insert(), {"name": "Fausta"})
        connection.execute(
            Customer.__table__.insert(),
            {"client_type": "company", "name": "Klientas", "company_code": "1"},
        )
    OrmBase.metadata.create_all(engine)
    with engine.connect() as connection:
        assert connection.execute(Company.__table__.select()).one().name == "Fausta"
        assert connection.execute(Customer.__table__.select()).one().name == "Klientas"
        assert set(Product.__table__.metadata.tables).issuperset(
            {"products", "product_categories", "units_of_measure", "product_barcodes"}
        )


def test_product_aggregate_crud_categories_units_and_barcodes(
    service: ProductService,
) -> None:
    category = service.add_category(" Biuro prekės ")
    assert service.add_category("BIURO PREKĖS").id == category.id
    product = service.save_product(
        None,
        values(
            service,
            category_id=category.id,
            barcodes=[
                {"barcode": "123", "barcode_type": "other", "is_default": True},
                {"barcode": "456", "barcode_type": "ean8", "is_default": False},
            ],
        ),
    )
    assert product.category.name == "Biuro prekės"
    assert product.unit.code == "vnt."
    assert len(product.barcodes) == 2 and product.default_barcode.barcode == "123"
    updated = service.save_product(
        product.id,
        values(
            service,
            name="Naujas",
            code="P-1",
            barcodes=[{"barcode": "456", "barcode_type": "ean8", "is_default": False}],
        ),
    )
    assert updated.name == "Naujas"
    assert updated.default_barcode.barcode == "456"
    service.deactivate_product(product.id)
    assert service.get_product(product.id).status == PRODUCT_STATUS_INACTIVE


def test_product_and_service_creation_defaults(service: ProductService) -> None:
    product = service.save_product(None, values(service))
    service_values = service.product_values(product_type=PRODUCT_TYPE_SERVICE)
    service_values.update({"name": "Konsultacija", "code": "S-1", "unit_price": "50"})
    service_item = service.save_product(None, service_values)
    assert product.product_type == PRODUCT_TYPE_PRODUCT
    assert service_item.product_type == PRODUCT_TYPE_SERVICE
    assert service_item.unit.code == "val."


def test_validation_duplicates_negative_price_and_barcodes(
    service: ProductService,
) -> None:
    service.save_product(
        None,
        values(
            service,
            barcodes=[{"barcode": "123", "barcode_type": "other", "is_default": True}],
        ),
    )
    with pytest.raises(ValueError, match="Pavadinimas"):
        service.save_product(None, values(service, name="", code="X"))
    with pytest.raises(ValueError, match="(?i)kaina"):
        service.save_product(None, values(service, code="X", unit_price="-1"))
    with pytest.raises(ValueError, match="kodu"):
        service.save_product(None, values(service, name="Kitas", code=" p-1 "))
    with pytest.raises(ValueError, match="barkodas"):
        service.save_product(
            None,
            values(
                service,
                code="X",
                barcodes=[{"barcode": "123", "barcode_type": "other"}],
            ),
        )
    with pytest.raises(ValueError, match="vienas numatytasis"):
        service.save_product(
            None,
            values(
                service,
                code="X",
                barcodes=[
                    {"barcode": "1", "barcode_type": "other", "is_default": True},
                    {"barcode": "2", "barcode_type": "other", "is_default": True},
                ],
            ),
        )


def test_vat_pricing_zero_and_not_object_are_distinct(service: ProductService) -> None:
    priced = service.save_product(None, values(service))
    assert priced.price_basis == PRICE_BASIS_NET
    assert priced.vat_treatment == VAT_TREATMENT_RATE and priced.vat_rate == Decimal(
        "21"
    )
    assert service.gross_price(
        Decimal("3.20"), VAT_TREATMENT_RATE, Decimal("21")
    ) == Decimal("3.87")
    assert service.gross_price(
        Decimal("0.01"), VAT_TREATMENT_RATE, Decimal("21")
    ) == Decimal("0.01")
    zero = service.save_product(
        None, values(service, name="Zero", code="Z", vat_rate="0")
    )
    not_object = service.save_product(
        None,
        values(
            service,
            name="Ne objektas",
            code="N",
            vat_treatment=VAT_TREATMENT_NOT_OBJECT,
            vat_rate="",
        ),
    )
    assert zero.vat_treatment == VAT_TREATMENT_RATE and zero.vat_rate == 0
    assert (
        not_object.vat_treatment == VAT_TREATMENT_NOT_OBJECT
        and not_object.vat_rate is None
    )


def test_non_vat_payer_uses_final_price(repository: ProductRepository) -> None:
    service = ProductService(repository, VatCompanyService(False))  # type: ignore[arg-type]
    service.ensure_default_units()
    product = service.save_product(
        None, values(service, vat_treatment=VAT_TREATMENT_RATE, vat_rate="21")
    )
    assert product.price_basis == PRICE_BASIS_FINAL
    assert product.vat_treatment == VAT_TREATMENT_NOT_APPLICABLE
    assert product.vat_rate is None


def test_search_filters_and_stable_sort(service: ProductService) -> None:
    category = service.add_category("Biuras")
    service.save_product(
        None,
        values(
            service,
            name="Žirklės",
            code="Z",
            category_id=category.id,
            barcodes=[{"barcode": "999", "barcode_type": "other"}],
        ),
    )
    service.save_product(
        None,
        values(
            service,
            name="Adata",
            code="A",
            product_type=PRODUCT_TYPE_SERVICE,
            status=PRODUCT_STATUS_INACTIVE,
        ),
    )
    assert [item.name for item in service.list_products()] == ["Adata", "Žirklės"]
    assert [item.name for item in service.list_products("999", status="active")] == [
        "Žirklės"
    ]
    assert [
        item.name for item in service.list_products("biuras", product_type="product")
    ] == ["Žirklės"]


def test_repository_rolls_back_failed_aggregate(
    repository: ProductRepository, service: ProductService
) -> None:
    first = service.save_product(None, values(service))
    product_values = {
        "name": "Broken",
        "code": "P-1",
        "product_type": first.product_type,
        "category_id": None,
        "unit_id": first.unit_id,
        "unit_price": first.unit_price,
        "price_basis": first.price_basis,
        "vat_treatment": first.vat_treatment,
        "vat_rate": first.vat_rate,
        "status": first.status,
        "notes": "",
    }
    barcodes: list[dict[str, object]] = []
    with pytest.raises(IntegrityError):
        repository.save(None, product_values, barcodes)
    assert [item.id for item in repository.list_all()] == [first.id]


class FakeView:
    SORT_FIELDS = ("name",)

    def __init__(self) -> None:
        self.controller = None
        self.products: list[Product] = []
        self.loading: list[bool] = []
        self.selected_id = None
        self.vat = None

    def bind_controller(self, controller):
        self.controller = controller

    def show(self):
        pass

    def set_loading(self, value):
        self.loading.append(value)

    def set_vat_payer(self, value):
        self.vat = value

    def display_products(self, products, _total):
        self.products = products

    def selected_product_id(self):
        return self.selected_id

    def selected_product(self):
        return next(
            (item for item in self.products if item.id == self.selected_id), None
        )

    def confirm_delete(self, _name):
        return True

    def show_error(self, message):
        raise AssertionError(message)


class FakeDialog:
    def __init__(self):
        self.controller = None
        self.product = None
        self.visible = False
        self.vat = None

    def bind_controller(self, controller):
        self.controller = controller

    def display_product(self, product, _values, _categories, _units, vat):
        self.product = product
        self.vat = vat

    def show(self):
        self.visible = True


def test_controller_load_create_edit_deactivate_and_vat(
    service: ProductService,
) -> None:
    view, dialog = FakeView(), FakeDialog()
    controller = ProductController(service, view, dialog)  # type: ignore[arg-type]
    controller.refresh()
    assert view.loading == [True, False] and view.vat is True
    controller.open_new_product()
    assert dialog.visible and dialog.product is None
    product = controller.save_product(None, values(service))
    view.selected_id = product.id
    controller.open_selected_product()
    assert dialog.product.id == product.id
    controller.deactivate_selected_product()
    assert service.get_product(product.id).status == PRODUCT_STATUS_INACTIVE
