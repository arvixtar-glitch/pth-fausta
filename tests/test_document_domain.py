"""Tests for the persistence-independent Document domain foundation."""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.models.document import (
    Document,
    DocumentInvariantViolation,
    DocumentValidationFailed,
    InvalidLifecycleTransition,
)
from app.models.document_types import (
    AcceptanceStatus,
    DeliveryStatus,
    DocumentType,
    LifecycleState,
    PaymentStatus,
    PriceBasis,
    VatTreatment,
    document_type_config,
)
from app.models.document_values import (
    BuyerSnapshot,
    DocumentCancelled,
    DocumentCopied,
    DocumentCreated,
    DocumentFinalized,
    DocumentLine,
    DocumentNumber,
    Money,
    Percentage,
    Quantity,
    SellerSnapshot,
    VatRate,
)
from app.services.document_domain_service import (
    DocumentTotalsService,
    DocumentValidationService,
)


class NumberProvider:
    """Return deterministic numbers for aggregate unit tests."""

    def __init__(self) -> None:
        self.calls = 0

    def next_number(
        self, document_type: DocumentType, series: str
    ) -> DocumentNumber:
        """Reserve the next test number."""
        self.calls += 1
        return DocumentNumber(series, self.calls, f"{series}-{self.calls:06d}")


@pytest.fixture
def calculator() -> DocumentTotalsService:
    return DocumentTotalsService()


@pytest.fixture
def validator() -> DocumentValidationService:
    return DocumentValidationService()


def line(
    *,
    description: str = "Konsultacija",
    quantity: str = "2",
    price: str = "100",
    basis: PriceBasis = PriceBasis.NET,
    discount: str = "10",
    treatment: VatTreatment = VatTreatment.STANDARD,
    vat_rate: str = "21",
) -> DocumentLine:
    return DocumentLine.create(
        position=99,
        description=description,
        unit="val.",
        quantity=Quantity(Decimal(quantity)),
        unit_price=Money(Decimal(price)),
        price_basis=basis,
        discount=Percentage(Decimal(discount)),
        vat_treatment=treatment,
        vat_rate=VatRate(Decimal(vat_rate)),
    )


def complete_document(
    calculator: DocumentTotalsService,
    document_type: DocumentType = DocumentType.INVOICE,
) -> Document:
    document = Document.create(
        document_type,
        document_date=date(2026, 7, 21),
        seller=SellerSnapshot(name="PTH Fausta", is_vat_payer=True),
        buyer=BuyerSnapshot(name="Klientas"),
    )
    due_date = (
        date(2026, 8, 1)
        if document_type_config(document_type).due_date_required
        else None
    )
    document.update_header(
        document_date=document.document_date,
        due_date=due_date,
        notes="Pastaba",
        external_order_number=(
            "EBAY-1" if document_type is DocumentType.EBAY_INVOICE else ""
        ),
    )
    document.add_line(line(), calculator)
    document.collect_events()
    return document


def test_all_supported_types_share_one_aggregate_and_explicit_config() -> None:
    documents = [
        Document.create(item, document_date=date.today()) for item in DocumentType
    ]
    assert len(documents) == 4
    assert all(type(document) is Document for document in documents)
    assert {
        document_type_config(document.document_type).default_series
        for document in documents
    } == {"SF", "IS", "KP", "EB"}
    assert documents[2].payment_status is PaymentStatus.NOT_APPLICABLE
    assert documents[3].external_order_number == ""


def test_new_document_is_identified_draft_without_official_number() -> None:
    document = Document.create(DocumentType.INVOICE, document_date=date.today())
    assert document.lifecycle is LifecycleState.DRAFT
    assert document.document_number is None
    event = document.collect_events()[0]
    assert isinstance(event, DocumentCreated)
    assert event.aggregate_id == document.id


def test_value_objects_and_snapshots_are_immutable() -> None:
    money = Money(Decimal("1.25"), "eur")
    assert money.currency == "EUR"
    with pytest.raises(FrozenInstanceError):
        money.amount = Decimal("2")  # type: ignore[misc]
    with pytest.raises(ValueError):
        Quantity(Decimal("-1"))
    with pytest.raises(ValueError):
        Percentage(Decimal("101"))
    with pytest.raises(ValueError):
        Money(Decimal("1"), "EU")


def test_lines_are_owned_ordered_and_totals_recalculate(
    calculator: DocumentTotalsService,
) -> None:
    document = Document.create(DocumentType.INVOICE, document_date=date.today())
    first, second = line(description="A"), line(description="B", discount="0")
    document.add_line(first, calculator)
    document.add_line(second, calculator)
    assert [item.position for item in document.lines] == [1, 2]
    assert document.totals.subtotal.amount == Decimal("400.00")
    assert document.totals.discount_total.amount == Decimal("20.00")
    assert document.totals.tax_total.amount == Decimal("79.80")
    assert document.totals.grand_total.amount == Decimal("459.80")
    document.move_line(second.id, 1, calculator)
    assert [item.description for item in document.lines] == ["B", "A"]
    document.remove_line(first.id, calculator)
    assert document.lines[0].position == 1
    assert document.totals.grand_total.amount == Decimal("242.00")


def test_net_gross_and_non_taxable_calculation_are_distinct(
    calculator: DocumentTotalsService,
) -> None:
    gross = calculator.calculate(
        (line(price="121", basis=PriceBasis.GROSS, discount="0"),), "EUR"
    )
    exempt = calculator.calculate(
        (
            line(
                price="100", discount="0", treatment=VatTreatment.EXEMPT,
                vat_rate="0",
            ),
        ),
        "EUR",
    )
    assert gross.taxable_amount.amount == Decimal("200.00")
    assert gross.tax_total.amount == Decimal("42.00")
    assert gross.grand_total.amount == Decimal("242.00")
    assert exempt.taxable_amount.amount == Decimal("0.00")
    assert exempt.tax_total.amount == Decimal("0.00")
    assert exempt.grand_total.amount == Decimal("200.00")


def test_structured_validation_allows_incomplete_draft_but_blocks_finalization(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    document = Document.create(DocumentType.INVOICE, document_date=date.today())
    assert validator.validate_draft(document).is_valid
    result = validator.validate_finalization(document)
    assert not result.is_valid
    assert {issue.code for issue in result.issues} == {
        "seller_name_required",
        "buyer_name_required",
        "line_required",
        "due_date_required",
    }
    provider = NumberProvider()
    with pytest.raises(DocumentValidationFailed) as error:
        document.finalize(validator, calculator, provider)
    assert error.value.result == result
    assert provider.calls == 0
    assert document.lifecycle is LifecycleState.DRAFT


def test_type_specific_validation_is_configuration_driven(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    offer = complete_document(calculator, DocumentType.COMMERCIAL_OFFER)
    ebay = complete_document(calculator, DocumentType.EBAY_INVOICE)
    ebay.update_header(
        document_date=ebay.document_date,
        due_date=ebay.due_date,
        notes="",
        external_order_number="",
    )
    assert validator.validate_finalization(offer).is_valid
    assert {
        issue.code for issue in validator.validate_finalization(ebay).issues
    } == {"external_order_number_required"}


def test_due_date_order_and_vat_combination_are_validated(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    document = complete_document(calculator)
    document.update_header(
        document_date=document.document_date,
        due_date=document.document_date - timedelta(days=1),
        notes="",
    )
    document.add_line(
        line(treatment=VatTreatment.ZERO_RATE, vat_rate="21"), calculator
    )
    assert {issue.code for issue in validator.validate_finalization(document).issues} == {
        "due_date_before_document_date",
        "invalid_vat_configuration",
    }


def test_non_vat_seller_cannot_finalize_vat_charging_lines(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    document = complete_document(calculator)
    document.replace_seller(SellerSnapshot(name="PTH Fausta"))
    assert {
        issue.code for issue in validator.validate_finalization(document).issues
    } == {"vat_not_applicable_for_seller"}


def test_finalization_freezes_content_and_emits_numbered_event(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    document = complete_document(calculator)
    provider = NumberProvider()
    document.finalize(validator, calculator, provider)
    assert document.lifecycle is LifecycleState.FINALIZED
    assert document.document_number == DocumentNumber("SF", 1, "SF-000001")
    assert document.metadata.finalized_at is not None
    event = document.collect_events()[0]
    assert isinstance(event, DocumentFinalized)
    assert event.document_number == "SF-000001"
    with pytest.raises(InvalidLifecycleTransition):
        document.update_header(
            document_date=date.today(), due_date=None, notes="changed"
        )
    with pytest.raises(InvalidLifecycleTransition):
        document.finalize(validator, calculator, provider)
    assert provider.calls == 1


def test_operational_statuses_remain_independent_after_finalization(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    document = complete_document(calculator)
    document.finalize(validator, calculator, NumberProvider())
    original_totals = document.totals
    document.update_operational_statuses(
        payment=PaymentStatus.PAID,
        delivery=DeliveryStatus.DELIVERED,
        acceptance=AcceptanceStatus.ACCEPTED,
    )
    assert document.lifecycle is LifecycleState.FINALIZED
    assert document.payment_status is PaymentStatus.PAID
    assert document.delivery_status is DeliveryStatus.DELIVERED
    assert document.acceptance_status is AcceptanceStatus.ACCEPTED
    assert document.totals == original_totals


def test_cancellation_requires_finalized_document_and_reason(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    document = complete_document(calculator)
    with pytest.raises(InvalidLifecycleTransition):
        document.cancel("Klaida")
    document.finalize(validator, calculator, NumberProvider())
    with pytest.raises(DocumentInvariantViolation):
        document.cancel(" ")
    document.cancel("Klaidingas pirkėjas")
    assert document.lifecycle is LifecycleState.CANCELLED
    assert document.metadata.cancellation_reason == "Klaidingas pirkėjas"
    assert document.document_number.formatted == "SF-000001"  # type: ignore[union-attr]
    assert isinstance(document.collect_events()[-1], DocumentCancelled)
    with pytest.raises(InvalidLifecycleTransition):
        document.cancel("Dar kartą")


def test_copy_is_independent_unnumbered_draft_from_every_state(
    validator: DocumentValidationService,
    calculator: DocumentTotalsService,
) -> None:
    source = complete_document(calculator)
    source.finalize(validator, calculator, NumberProvider())
    copied = source.copy_as_draft()
    assert copied.id != source.id
    assert copied.lifecycle is LifecycleState.DRAFT
    assert copied.document_number is None
    assert copied.lines[0].id != source.lines[0].id
    assert copied.lines[0].description == source.lines[0].description
    event = copied.collect_events()[0]
    assert isinstance(event, DocumentCopied)
    assert event.source_document_id == source.id


def test_document_currency_and_line_currency_must_match(
    calculator: DocumentTotalsService,
) -> None:
    document = Document.create(DocumentType.INVOICE, document_date=date.today())
    usd_line = DocumentLine.create(
        position=1,
        description="USD",
        unit="vnt.",
        quantity=Quantity(Decimal("1")),
        unit_price=Money(Decimal("1"), "USD"),
        price_basis=PriceBasis.NET,
        vat_treatment=VatTreatment.ZERO_RATE,
        vat_rate=VatRate(Decimal("0")),
    )
    with pytest.raises(DocumentInvariantViolation):
        document.add_line(usd_line, calculator)
