"""Immutable values owned by the Document aggregate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.models.document_types import PriceBasis, VatTreatment


ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


@dataclass(frozen=True, slots=True)
class Money:
    """Represent a currency-qualified accounting amount."""

    amount: Decimal
    currency: str = "EUR"

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", Decimal(str(self.amount)))
        normalized_currency = self.currency.strip().upper()
        if len(normalized_currency) != 3:
            raise ValueError("Currency must use a three-letter code.")
        object.__setattr__(self, "currency", normalized_currency)

    @classmethod
    def zero(cls, currency: str = "EUR") -> Money:
        """Create a zero amount in the requested currency."""
        return cls(ZERO, currency)

    def _require_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError("Money currencies must match.")

    def __add__(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.amount - other.amount, self.currency)


@dataclass(frozen=True, slots=True)
class Quantity:
    """Represent a non-negative business quantity."""

    value: Decimal

    def __post_init__(self) -> None:
        value = Decimal(str(self.value))
        if value < ZERO:
            raise ValueError("Quantity cannot be negative.")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class Percentage:
    """Represent a percentage from zero through one hundred."""

    value: Decimal

    def __post_init__(self) -> None:
        value = Decimal(str(self.value))
        if not ZERO <= value <= ONE_HUNDRED:
            raise ValueError("Percentage must be between 0 and 100.")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class VatRate:
    """Represent a configured VAT percentage."""

    value: Decimal

    def __post_init__(self) -> None:
        value = Decimal(str(self.value))
        if not ZERO <= value <= ONE_HUNDRED:
            raise ValueError("VAT rate must be between 0 and 100.")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class DocumentNumber:
    """Represent an immutable official document number."""

    series: str
    sequence: int
    formatted: str

    def __post_init__(self) -> None:
        if not self.series.strip() or self.sequence <= 0 or not self.formatted.strip():
            raise ValueError("A complete official document number is required.")


@dataclass(frozen=True, slots=True)
class SellerSnapshot:
    """Preserve the seller data printed on a document."""

    name: str = ""
    company_code: str = ""
    vat_code: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    bank_name: str = ""
    iban: str = ""
    swift_bic: str = ""
    account_holder: str = ""
    is_vat_payer: bool = False


@dataclass(frozen=True, slots=True)
class BuyerSnapshot:
    """Preserve the buyer data printed on a document."""

    name: str = ""
    company_code: str = ""
    vat_code: str = ""
    address: str = ""
    email: str = ""
    phone: str = ""


@dataclass(frozen=True, slots=True)
class TaxSnapshot:
    """Preserve the tax context used to issue a document."""

    seller_is_vat_payer: bool


@dataclass(frozen=True, slots=True)
class PresentationSnapshot:
    """Preserve presentation settings used for historical rendering."""

    language: str = "lt"
    template: str = "default"


@dataclass(frozen=True, slots=True)
class DocumentLine:
    """Represent one independently reproducible document line."""

    id: UUID
    position: int
    item_code: str
    description: str
    unit: str
    quantity: Quantity
    unit_price: Money
    price_basis: PriceBasis
    discount: Percentage
    vat_treatment: VatTreatment
    vat_rate: VatRate
    product_id: int | None = None

    @classmethod
    def create(
        cls,
        *,
        position: int,
        description: str,
        unit: str,
        quantity: Quantity,
        unit_price: Money,
        price_basis: PriceBasis,
        vat_treatment: VatTreatment,
        vat_rate: VatRate,
        item_code: str = "",
        discount: Percentage = Percentage(ZERO),
        product_id: int | None = None,
    ) -> DocumentLine:
        """Create a document-owned line with a new immutable identity."""
        return cls(
            uuid4(), position, item_code.strip(), description.strip(), unit.strip(),
            quantity, unit_price, price_basis, discount, vat_treatment, vat_rate,
            product_id,
        )


@dataclass(frozen=True, slots=True)
class DocumentTotals:
    """Contain calculated, read-only aggregate totals."""

    subtotal: Money
    discount_total: Money
    taxable_amount: Money
    tax_total: Money
    grand_total: Money

    @classmethod
    def zero(cls, currency: str) -> DocumentTotals:
        """Create empty totals in one document currency."""
        zero = Money.zero(currency)
        return cls(zero, zero, zero, zero, zero)


@dataclass(frozen=True, slots=True)
class Metadata:
    """Contain system-maintained document lifecycle metadata."""

    created_at: datetime
    updated_at: datetime
    finalized_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None

    @classmethod
    def create(cls) -> Metadata:
        """Create UTC metadata for a new aggregate."""
        now = datetime.now(UTC)
        return cls(now, now)


class ValidationSeverity(StrEnum):
    """Define validation feedback importance."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Describe one structured validation finding."""

    field: str
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    blocking: bool = True


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Collect structured validation findings without mutating a document."""

    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        """Return whether no blocking issue exists."""
        return not any(issue.blocking for issue in self.issues)


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Represent an immutable completed document-domain fact."""

    aggregate_id: UUID
    occurred_at: datetime
    event_id: UUID


@dataclass(frozen=True, slots=True)
class DocumentCreated(DomainEvent):
    """Report successful creation of a draft."""

    document_type: str


@dataclass(frozen=True, slots=True)
class DocumentUpdated(DomainEvent):
    """Report a meaningful draft business change."""


@dataclass(frozen=True, slots=True)
class DocumentFinalized(DomainEvent):
    """Report successful issuance of a document."""

    document_type: str
    document_number: str


@dataclass(frozen=True, slots=True)
class DocumentCancelled(DomainEvent):
    """Report successful cancellation of an issued document."""

    document_number: str


@dataclass(frozen=True, slots=True)
class DocumentCopied(DomainEvent):
    """Report creation of an independent draft copy."""

    source_document_id: UUID


def event_identity() -> tuple[datetime, UUID]:
    """Return the shared system values required by a new domain event."""
    return datetime.now(UTC), uuid4()
