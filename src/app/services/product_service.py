"""Product aggregate business rules, pricing, and list operations."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from app.models.product import (
    PRICE_BASIS_FINAL,
    PRICE_BASIS_NET,
    PRODUCT_STATUS_ACTIVE,
    PRODUCT_STATUS_INACTIVE,
    PRODUCT_TYPE_PRODUCT,
    PRODUCT_TYPE_SERVICE,
    VAT_TREATMENT_NOT_APPLICABLE,
    VAT_TREATMENT_NOT_OBJECT,
    VAT_TREATMENT_RATE,
    Product,
    ProductCategory,
    UnitOfMeasure,
)
from app.repositories.product_repository import ProductRepository
from app.services.base_service import BaseService
from app.services.company_service import CompanyService

MONEY = Decimal("0.01")
VAT_RATES = {Decimal("21"), Decimal("9"), Decimal("5"), Decimal("0")}
PRODUCT_TYPES = {PRODUCT_TYPE_PRODUCT, PRODUCT_TYPE_SERVICE}
PRODUCT_STATUSES = {PRODUCT_STATUS_ACTIVE, PRODUCT_STATUS_INACTIVE}
BARCODE_TYPES = {"ean13", "ean8", "upca", "other"}
DEFAULT_UNITS = (
    ("vnt.", "vnt."),
    ("kg", "kg"),
    ("g", "g"),
    ("m", "m"),
    ("m²", "m²"),
    ("m³", "m³"),
    ("l", "l"),
    ("val.", "val."),
    ("d.", "d."),
    ("mėn.", "mėn."),
    ("kompl.", "kompl."),
    ("pasl.", "pasl."),
)
SORTABLE_FIELDS = {
    "name",
    "code",
    "product_type",
    "unit",
    "unit_price",
    "vat_rate",
    "status",
}


class ProductService(BaseService):
    """Manage product CRUD and preserve aggregate invariants."""

    def __init__(
        self, repository: ProductRepository, company_service: CompanyService
    ) -> None:
        self._repository = repository
        self._company_service = company_service

    def ensure_default_units(self) -> None:
        existing = {unit.code for unit in self._repository.list_units()}
        for code, name in DEFAULT_UNITS:
            if code not in existing:
                self._repository.create_unit(code, name)

    def is_vat_payer(self) -> bool:
        return self._company_service.is_vat_payer()

    def list_categories(self) -> list[ProductCategory]:
        return self._repository.list_categories()

    def add_category(self, name: str) -> ProductCategory:
        clean_name = " ".join(name.split())
        normalized = self._normalize(clean_name)
        if not normalized:
            raise ValueError("Įveskite kategorijos pavadinimą.")
        existing = next(
            (
                item
                for item in self.list_categories()
                if item.normalized_name == normalized
            ),
            None,
        )
        return existing or self._repository.create_category(clean_name, normalized)

    def list_units(self) -> list[UnitOfMeasure]:
        self.ensure_default_units()
        return self._repository.list_units()

    def get_product(self, product_id: int) -> Product:
        product = self._repository.get(product_id)
        if product is None:
            raise LookupError("Prekė ar paslauga nerasta.")
        return product

    def list_products(
        self,
        query: str = "",
        product_type: str | None = None,
        status: str | None = None,
        sort_by: str = "name",
        descending: bool = False,
    ) -> list[Product]:
        if product_type not in (None, *PRODUCT_TYPES):
            raise ValueError("Neteisingas tipo filtras.")
        if status not in (None, *PRODUCT_STATUSES):
            raise ValueError("Neteisingas būsenos filtras.")
        if sort_by not in SORTABLE_FIELDS:
            raise ValueError("Neteisingas rūšiavimo laukas.")
        normalized_query = self._normalize(query)
        products = [
            item
            for item in self._repository.list_all()
            if (product_type is None or item.product_type == product_type)
            and (status is None or item.status == status)
            and (not normalized_query or normalized_query in self._search_text(item))
        ]

        def key(item: Product) -> object:
            value: object
            if sort_by == "unit":
                value = item.unit.code
            else:
                value = getattr(item, sort_by)
            if sort_by in {"unit_price", "vat_rate"}:
                return value if value is not None else Decimal("-1")
            return self._normalize(str(value or ""))

        return sorted(products, key=key, reverse=descending)

    def count_products(self) -> int:
        return len(self._repository.list_all())

    def save_product(self, product_id: int | None, values: dict[str, Any]) -> Product:
        if product_id is not None:
            self.get_product(product_id)
        product_values, barcodes = self._validate(values, product_id)
        return self._repository.save(product_id, product_values, barcodes)

    def deactivate_product(self, product_id: int) -> Product:
        self.get_product(product_id)
        return self._repository.set_status(product_id, PRODUCT_STATUS_INACTIVE)

    def gross_price(
        self, net_price: Decimal, treatment: str, rate: Decimal | None
    ) -> Decimal:
        net = self._money(net_price)
        if treatment != VAT_TREATMENT_RATE or rate is None:
            return net
        return (net * (Decimal("1") + rate / Decimal("100"))).quantize(
            MONEY, rounding=ROUND_HALF_UP
        )

    def product_values(
        self, product: Product | None = None, product_type: str = PRODUCT_TYPE_PRODUCT
    ) -> dict[str, Any]:
        if product is None:
            units = self.list_units()
            default_code = "val." if product_type == PRODUCT_TYPE_SERVICE else "vnt."
            unit = next((item for item in units if item.code == default_code), units[0])
            return {
                "product_type": product_type,
                "name": "",
                "code": "",
                "category_id": None,
                "unit_id": unit.id,
                "unit_price": "0.00",
                "vat_treatment": VAT_TREATMENT_RATE
                if self.is_vat_payer()
                else VAT_TREATMENT_NOT_APPLICABLE,
                "vat_rate": "21" if self.is_vat_payer() else "",
                "status": PRODUCT_STATUS_ACTIVE,
                "notes": "",
                "barcodes": [],
            }
        return {
            "product_type": product.product_type,
            "name": product.name,
            "code": product.code or "",
            "category_id": product.category_id,
            "unit_id": product.unit_id,
            "unit_price": f"{product.unit_price:.2f}",
            "vat_treatment": product.vat_treatment,
            "vat_rate": "" if product.vat_rate is None else f"{product.vat_rate:g}",
            "status": product.status,
            "notes": product.notes,
            "barcodes": [
                {
                    "barcode": item.barcode,
                    "barcode_type": item.barcode_type,
                    "is_default": item.is_default,
                }
                for item in product.barcodes
            ],
        }

    def _validate(
        self, values: dict[str, Any], product_id: int | None
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        product_type = str(values.get("product_type", ""))
        name = " ".join(str(values.get("name", "")).split())
        code = " ".join(str(values.get("code", "")).split()) or None
        status = str(values.get("status", PRODUCT_STATUS_ACTIVE))
        if product_type not in PRODUCT_TYPES:
            raise ValueError("Pasirinkite teisingą prekės ar paslaugos tipą.")
        if not name:
            raise ValueError("Pavadinimas yra privalomas.")
        if status not in PRODUCT_STATUSES:
            raise ValueError("Pasirinkite teisingą būseną.")
        try:
            category_id = (
                int(values["category_id"]) if values.get("category_id") else None
            )
            unit_id = int(values["unit_id"])
        except (TypeError, ValueError, KeyError) as error:
            raise ValueError("Pasirinkite matavimo vienetą.") from error
        if category_id and not any(
            item.id == category_id for item in self.list_categories()
        ):
            raise ValueError("Pasirinkta kategorija nerasta.")
        if not any(item.id == unit_id for item in self.list_units()):
            raise ValueError("Pasirinktas matavimo vienetas nerastas.")
        price = self._money(values.get("unit_price", "0"))
        if price < 0:
            raise ValueError("Kaina negali būti neigiama.")
        vat_treatment, vat_rate, price_basis = self._pricing(values)
        self._ensure_unique_code(code, product_id)
        barcodes = self._validate_barcodes(values.get("barcodes", []), product_id)
        return (
            {
                "product_type": product_type,
                "name": name,
                "code": code,
                "category_id": category_id,
                "unit_id": unit_id,
                "unit_price": price,
                "price_basis": price_basis,
                "vat_treatment": vat_treatment,
                "vat_rate": vat_rate,
                "status": status,
                "notes": str(values.get("notes", "")).strip(),
            },
            barcodes,
        )

    def _pricing(self, values: dict[str, Any]) -> tuple[str, Decimal | None, str]:
        if not self.is_vat_payer():
            return VAT_TREATMENT_NOT_APPLICABLE, None, PRICE_BASIS_FINAL
        treatment = str(values.get("vat_treatment", ""))
        if treatment == VAT_TREATMENT_NOT_OBJECT:
            return treatment, None, PRICE_BASIS_NET
        if treatment != VAT_TREATMENT_RATE:
            raise ValueError("Pasirinkite PVM taikymo būdą.")
        try:
            rate = Decimal(str(values.get("vat_rate", "")))
        except InvalidOperation as error:
            raise ValueError("Pasirinkite PVM tarifą.") from error
        if rate not in VAT_RATES:
            raise ValueError("Pasirinkite galiojantį PVM tarifą.")
        return treatment, rate, PRICE_BASIS_NET

    def _validate_barcodes(
        self, values: object, product_id: int | None
    ) -> list[dict[str, Any]]:
        if not isinstance(values, list):
            raise ValueError("Neteisingi barkodų duomenys.")
        cleaned: list[dict[str, Any]] = []
        defaults = 0
        seen: set[str] = set()
        existing = {
            item.barcode: item.product_id
            for product in self._repository.list_all()
            for item in product.barcodes
        }
        for value in values:
            if not isinstance(value, dict):
                raise ValueError("Neteisingi barkodų duomenys.")
            barcode = "".join(str(value.get("barcode", "")).split())
            barcode_type = str(value.get("barcode_type", "other"))
            is_default = bool(value.get("is_default", False))
            if not barcode:
                raise ValueError("Barkodas negali būti tuščias.")
            if barcode_type not in BARCODE_TYPES:
                raise ValueError("Pasirinkite barkodo tipą.")
            if barcode in seen or (
                barcode in existing and existing[barcode] != product_id
            ):
                raise ValueError("Toks barkodas jau egzistuoja.")
            seen.add(barcode)
            defaults += int(is_default)
            cleaned.append(
                {
                    "barcode": barcode,
                    "barcode_type": barcode_type,
                    "is_default": is_default,
                }
            )
        if defaults > 1:
            raise ValueError("Galimas tik vienas numatytasis barkodas.")
        if cleaned and defaults == 0:
            cleaned[0]["is_default"] = True
        return cleaned

    def _ensure_unique_code(self, code: str | None, product_id: int | None) -> None:
        if not code:
            return
        normalized = self._normalize(code)
        if any(
            item.id != product_id and self._normalize(item.code or "") == normalized
            for item in self._repository.list_all()
        ):
            raise ValueError("Prekė ar paslauga su tokiu kodu jau egzistuoja.")

    def _search_text(self, product: Product) -> str:
        return " ".join(
            (
                self._normalize(product.name),
                self._normalize(product.code or ""),
                self._normalize(product.category.name if product.category else ""),
                *(self._normalize(item.barcode) for item in product.barcodes),
            )
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.casefold().split())

    @staticmethod
    def _money(value: object) -> Decimal:
        try:
            return Decimal(str(value).replace(",", ".")).quantize(
                MONEY, rounding=ROUND_HALF_UP
            )
        except InvalidOperation as error:
            raise ValueError("Įveskite teisingą kainą.") from error
