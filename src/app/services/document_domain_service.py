"""Stateless calculation and validation services for Document aggregates."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.models.document import Document
from app.models.document_types import PriceBasis, VatTreatment, document_type_config
from app.models.document_values import (
    DocumentLine,
    DocumentTotals,
    Money,
    ValidationIssue,
    ValidationResult,
)


ACCOUNTING_QUANTUM = Decimal("0.01")
ONE_HUNDRED = Decimal("100")
ZERO = Decimal("0")


class DocumentTotalsService:
    """Calculate deterministic line and document totals with Decimal."""

    @staticmethod
    def _round(value: Decimal) -> Decimal:
        return value.quantize(ACCOUNTING_QUANTUM, rounding=ROUND_HALF_UP)

    def calculate(
        self, lines: tuple[DocumentLine, ...], currency: str
    ) -> DocumentTotals:
        """Calculate authoritative totals from the complete line collection."""
        subtotal = ZERO
        discount_total = ZERO
        taxable_amount = ZERO
        tax_total = ZERO
        grand_total = ZERO
        for line in lines:
            if line.unit_price.currency != currency:
                raise ValueError("Line currency must match document currency.")
            values = self._calculate_line(line)
            subtotal += values[0]
            discount_total += values[1]
            taxable_amount += values[2]
            tax_total += values[3]
            grand_total += values[4]
        return DocumentTotals(
            Money(self._round(subtotal), currency),
            Money(self._round(discount_total), currency),
            Money(self._round(taxable_amount), currency),
            Money(self._round(tax_total), currency),
            Money(self._round(grand_total), currency),
        )

    def _calculate_line(
        self, line: DocumentLine
    ) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        entered = line.quantity.value * line.unit_price.amount
        discount = entered * line.discount.value / ONE_HUNDRED
        discounted = entered - discount
        taxable = line.vat_treatment in {
            VatTreatment.STANDARD,
            VatTreatment.ZERO_RATE,
        }
        if line.price_basis is PriceBasis.GROSS and taxable:
            divisor = Decimal("1") + line.vat_rate.value / ONE_HUNDRED
            net = discounted / divisor
            tax = discounted - net
            return entered, discount, net, tax, discounted
        net = discounted
        tax = (
            net * line.vat_rate.value / ONE_HUNDRED
            if line.vat_treatment is VatTreatment.STANDARD
            else ZERO
        )
        return entered, discount, net if taxable else ZERO, tax, net + tax


class DocumentValidationService:
    """Return structured findings without modifying the aggregate."""

    def validate_draft(self, document: Document) -> ValidationResult:
        """Validate invariants required for a persistable incomplete draft."""
        issues: list[ValidationIssue] = []
        for index, line in enumerate(document.lines, start=1):
            issues.extend(self._line_issues(line, index))
        return ValidationResult(tuple(issues))

    def validate_finalization(self, document: Document) -> ValidationResult:
        """Validate all common and configured rules required for issuance."""
        issues = list(self.validate_draft(document).issues)
        config = document_type_config(document.document_type)
        if not document.seller.name.strip():
            issues.append(self._required("seller.name", "seller_name_required"))
        if config.buyer_required and not document.buyer.name.strip():
            issues.append(self._required("buyer.name", "buyer_name_required"))
        if not document.lines:
            issues.append(self._required("lines", "line_required"))
        if config.due_date_required and document.due_date is None:
            issues.append(self._required("due_date", "due_date_required"))
        if (
            document.due_date is not None
            and document.due_date < document.document_date
        ):
            issues.append(
                ValidationIssue(
                    "due_date", "due_date_before_document_date",
                    "Due date cannot be earlier than document date.",
                )
            )
        if config.external_order_required and not document.external_order_number:
            issues.append(
                self._required(
                    "external_order_number", "external_order_number_required"
                )
            )
        if not document.seller.is_vat_payer:
            for index, line in enumerate(document.lines, start=1):
                if line.vat_treatment is not VatTreatment.NOT_APPLICABLE:
                    issues.append(
                        ValidationIssue(
                            f"lines.{index}.vat",
                            "vat_not_applicable_for_seller",
                            "A non-VAT seller cannot charge VAT.",
                        )
                    )
        return ValidationResult(tuple(issues))

    @staticmethod
    def _required(field: str, code: str) -> ValidationIssue:
        return ValidationIssue(field, code, "Required value is missing.")

    def _line_issues(
        self, line: DocumentLine, index: int
    ) -> list[ValidationIssue]:
        prefix = f"lines.{index}"
        issues: list[ValidationIssue] = []
        if not line.description:
            issues.append(self._required(f"{prefix}.description", "description_required"))
        if not line.unit:
            issues.append(self._required(f"{prefix}.unit", "unit_required"))
        if line.quantity.value <= ZERO:
            issues.append(
                ValidationIssue(
                    f"{prefix}.quantity", "quantity_must_be_positive",
                    "Quantity must be greater than zero.",
                )
            )
        if line.unit_price.amount < ZERO:
            issues.append(
                ValidationIssue(
                    f"{prefix}.unit_price", "price_must_not_be_negative",
                    "Unit price cannot be negative.",
                )
            )
        if not self._vat_is_consistent(line):
            issues.append(
                ValidationIssue(
                    f"{prefix}.vat", "invalid_vat_configuration",
                    "VAT treatment and rate are inconsistent.",
                )
            )
        return issues

    @staticmethod
    def _vat_is_consistent(line: DocumentLine) -> bool:
        if line.vat_treatment is VatTreatment.STANDARD:
            return line.vat_rate.value > ZERO
        if line.vat_treatment is VatTreatment.ZERO_RATE:
            return line.vat_rate.value == ZERO
        return line.vat_rate.value == ZERO
