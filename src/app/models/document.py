"""Persistence-independent Document aggregate and domain exceptions."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime
from typing import Protocol
from uuid import UUID, uuid4

from app.models.document_types import (
    AcceptanceStatus,
    DeliveryStatus,
    DocumentType,
    LifecycleState,
    PaymentStatus,
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
    DocumentTotals,
    DocumentUpdated,
    DomainEvent,
    Metadata,
    PresentationSnapshot,
    SellerSnapshot,
    TaxSnapshot,
    ValidationResult,
    event_identity,
)


class DocumentDomainError(Exception):
    """Base class for expected document business-rule violations."""


class InvalidLifecycleTransition(DocumentDomainError):
    """Report an operation that is invalid for the current lifecycle."""


class DocumentValidationFailed(DocumentDomainError):
    """Report structured finalization-validation failure."""

    def __init__(self, result: ValidationResult) -> None:
        super().__init__("Document finalization validation failed.")
        self.result = result


class DocumentInvariantViolation(DocumentDomainError):
    """Report an attempted violation of aggregate consistency."""


class MissingNumberSeries(DocumentDomainError):
    """Report unavailable numbering configuration during finalization."""


class NumberProvider(Protocol):
    """Define official-number allocation required by finalization."""

    def next_number(
        self, document_type: DocumentType, series: str
    ) -> DocumentNumber:
        """Return one atomically reserved official number."""


class TotalsCalculator(Protocol):
    """Define deterministic document financial calculation."""

    def calculate(
        self, lines: tuple[DocumentLine, ...], currency: str
    ) -> DocumentTotals:
        """Calculate totals for the complete ordered line collection."""


class DocumentValidator(Protocol):
    """Define structured domain validation."""

    def validate_draft(self, document: Document) -> ValidationResult:
        """Validate only invariants required to keep a draft."""

    def validate_finalization(self, document: Document) -> ValidationResult:
        """Validate all rules required to issue a document."""


class Document:
    """Protect the complete business-document consistency boundary."""

    def __init__(
        self,
        *,
        document_id: UUID,
        document_type: DocumentType,
        document_date: date,
        currency: str,
        seller: SellerSnapshot,
        buyer: BuyerSnapshot,
        presentation: PresentationSnapshot,
        metadata: Metadata,
    ) -> None:
        self._id = document_id
        self._document_type = document_type
        self._lifecycle = LifecycleState.DRAFT
        self._document_number: DocumentNumber | None = None
        self._document_date = document_date
        self._due_date: date | None = None
        self._currency = currency.strip().upper()
        if len(self._currency) != 3:
            raise DocumentInvariantViolation("Document currency must be valid.")
        self._seller = seller
        self._buyer = buyer
        self._tax = TaxSnapshot(seller.is_vat_payer)
        self._presentation = presentation
        self._lines: list[DocumentLine] = []
        self._totals = DocumentTotals.zero(self._currency)
        self._metadata = metadata
        config = document_type_config(document_type)
        self._payment_status = config.default_payment_status
        self._delivery_status = DeliveryStatus.NOT_SENT
        self._acceptance_status = config.default_acceptance_status
        self._notes = ""
        self._external_source = "ebay" if document_type is DocumentType.EBAY_INVOICE else ""
        self._external_order_number = ""
        self._events: list[DomainEvent] = []

    @classmethod
    def create(
        cls,
        document_type: DocumentType,
        *,
        document_date: date,
        currency: str = "EUR",
        seller: SellerSnapshot = SellerSnapshot(),
        buyer: BuyerSnapshot = BuyerSnapshot(),
        presentation: PresentationSnapshot = PresentationSnapshot(),
    ) -> Document:
        """Create a uniquely identified, unnumbered draft aggregate."""
        document = cls(
            document_id=uuid4(), document_type=document_type,
            document_date=document_date, currency=currency, seller=seller,
            buyer=buyer, presentation=presentation, metadata=Metadata.create(),
        )
        occurred_at, event_id = event_identity()
        document._events.append(
            DocumentCreated(
                document.id, occurred_at, event_id, document.document_type.value
            )
        )
        return document

    @property
    def id(self) -> UUID:
        """Return the immutable aggregate identity."""
        return self._id

    @property
    def document_type(self) -> DocumentType:
        """Return the current business-document type."""
        return self._document_type

    @property
    def lifecycle(self) -> LifecycleState:
        """Return the current accounting lifecycle state."""
        return self._lifecycle

    @property
    def document_number(self) -> DocumentNumber | None:
        """Return the official number, absent for drafts."""
        return self._document_number

    @property
    def document_date(self) -> date:
        """Return the business issue date."""
        return self._document_date

    @property
    def due_date(self) -> date | None:
        """Return the explicit payment due date when applicable."""
        return self._due_date

    @property
    def currency(self) -> str:
        """Return the single document currency."""
        return self._currency

    @property
    def seller(self) -> SellerSnapshot:
        """Return the aggregate-owned seller snapshot."""
        return self._seller

    @property
    def buyer(self) -> BuyerSnapshot:
        """Return the aggregate-owned buyer snapshot."""
        return self._buyer

    @property
    def tax(self) -> TaxSnapshot:
        """Return the aggregate-owned tax snapshot."""
        return self._tax

    @property
    def lines(self) -> tuple[DocumentLine, ...]:
        """Return ordered document lines as an immutable collection."""
        return tuple(self._lines)

    @property
    def totals(self) -> DocumentTotals:
        """Return calculated, read-only document totals."""
        return self._totals

    @property
    def metadata(self) -> Metadata:
        """Return system-maintained lifecycle metadata."""
        return self._metadata

    @property
    def payment_status(self) -> PaymentStatus:
        """Return the independent payment state."""
        return self._payment_status

    @property
    def delivery_status(self) -> DeliveryStatus:
        """Return the independent delivery state."""
        return self._delivery_status

    @property
    def acceptance_status(self) -> AcceptanceStatus:
        """Return the independent acceptance state."""
        return self._acceptance_status

    @property
    def notes(self) -> str:
        """Return notes that belong to reproducible printed content."""
        return self._notes

    @property
    def external_order_number(self) -> str:
        """Return the external order reference when applicable."""
        return self._external_order_number

    def _require_draft(self) -> None:
        if self.lifecycle is not LifecycleState.DRAFT:
            raise InvalidLifecycleTransition("Only a draft can be edited.")

    def _touch(self) -> None:
        now = datetime.now(UTC)
        self._metadata = replace(self._metadata, updated_at=now)
        occurred_at, event_id = event_identity()
        self._events.append(DocumentUpdated(self.id, occurred_at, event_id))

    def update_header(
        self,
        *,
        document_date: date,
        due_date: date | None,
        notes: str,
        external_order_number: str = "",
    ) -> None:
        """Update editable header values while preserving lifecycle rules."""
        self._require_draft()
        self._document_date = document_date
        self._due_date = due_date
        self._notes = notes.strip()
        self._external_order_number = external_order_number.strip()
        self._touch()

    def change_type(self, document_type: DocumentType) -> None:
        """Change a draft type and reset incompatible process defaults."""
        self._require_draft()
        self._document_type = document_type
        config = document_type_config(document_type)
        self._payment_status = config.default_payment_status
        self._acceptance_status = config.default_acceptance_status
        self._external_source = (
            "ebay" if document_type is DocumentType.EBAY_INVOICE else ""
        )
        if not config.payment_applicable:
            self._due_date = None
        self._touch()

    def replace_seller(self, seller: SellerSnapshot) -> None:
        """Explicitly replace draft seller data and tax context."""
        self._require_draft()
        self._seller = seller
        self._tax = TaxSnapshot(seller.is_vat_payer)
        self._touch()

    def replace_buyer(self, buyer: BuyerSnapshot) -> None:
        """Explicitly replace draft buyer data."""
        self._require_draft()
        self._buyer = buyer
        self._touch()

    def add_line(self, line: DocumentLine, calculator: TotalsCalculator) -> None:
        """Add an owned line, normalize ordering and recalculate totals."""
        self._require_draft()
        if line.unit_price.currency != self.currency:
            raise DocumentInvariantViolation("Line currency must match document.")
        self._lines.append(line)
        self._renumber_lines()
        self._recalculate(calculator)
        self._touch()

    def replace_line(
        self, line_id: UUID, replacement: DocumentLine, calculator: TotalsCalculator
    ) -> None:
        """Replace one owned draft line and recalculate totals."""
        self._require_draft()
        index = self._line_index(line_id)
        self._lines[index] = replace(replacement, id=line_id, position=index + 1)
        self._recalculate(calculator)
        self._touch()

    def remove_line(self, line_id: UUID, calculator: TotalsCalculator) -> None:
        """Remove one owned draft line and recalculate totals."""
        self._require_draft()
        self._lines.pop(self._line_index(line_id))
        self._renumber_lines()
        self._recalculate(calculator)
        self._touch()

    def move_line(
        self, line_id: UUID, new_position: int, calculator: TotalsCalculator
    ) -> None:
        """Move one line to an explicit one-based business position."""
        self._require_draft()
        if not 1 <= new_position <= len(self._lines):
            raise DocumentInvariantViolation("Line position is outside the document.")
        line = self._lines.pop(self._line_index(line_id))
        self._lines.insert(new_position - 1, line)
        self._renumber_lines()
        self._recalculate(calculator)
        self._touch()

    def _line_index(self, line_id: UUID) -> int:
        for index, line in enumerate(self._lines):
            if line.id == line_id:
                return index
        raise DocumentInvariantViolation("Line does not belong to this document.")

    def _renumber_lines(self) -> None:
        self._lines = [
            replace(line, position=index)
            for index, line in enumerate(self._lines, start=1)
        ]

    def _recalculate(self, calculator: TotalsCalculator) -> None:
        self._totals = calculator.calculate(self.lines, self.currency)

    def finalize(
        self,
        validator: DocumentValidator,
        calculator: TotalsCalculator,
        number_provider: NumberProvider,
        *,
        series: str | None = None,
    ) -> None:
        """Validate, calculate, number and freeze a complete draft."""
        self._require_draft()
        result = validator.validate_finalization(self)
        if not result.is_valid:
            raise DocumentValidationFailed(result)
        self._recalculate(calculator)
        resolved_series = (series or document_type_config(self.document_type).default_series).strip()
        if not resolved_series:
            raise MissingNumberSeries("A numbering series is required.")
        number = number_provider.next_number(self.document_type, resolved_series)
        now = datetime.now(UTC)
        self._document_number = number
        self._lifecycle = LifecycleState.FINALIZED
        self._metadata = replace(
            self._metadata, updated_at=now, finalized_at=now,
            cancelled_at=None, cancellation_reason=None,
        )
        occurred_at, event_id = event_identity()
        self._events.append(
            DocumentFinalized(
                self.id, occurred_at, event_id, self.document_type.value,
                number.formatted,
            )
        )

    def cancel(self, reason: str) -> None:
        """Cancel an issued document while preserving all historical content."""
        if self.lifecycle is not LifecycleState.FINALIZED:
            raise InvalidLifecycleTransition("Only a finalized document can be cancelled.")
        cancellation_reason = reason.strip()
        if not cancellation_reason:
            raise DocumentInvariantViolation("Cancellation reason is required.")
        now = datetime.now(UTC)
        self._lifecycle = LifecycleState.CANCELLED
        self._metadata = replace(
            self._metadata, updated_at=now, cancelled_at=now,
            cancellation_reason=cancellation_reason,
        )
        occurred_at, event_id = event_identity()
        assert self.document_number is not None
        self._events.append(
            DocumentCancelled(
                self.id, occurred_at, event_id, self.document_number.formatted
            )
        )

    def update_operational_statuses(
        self,
        *,
        payment: PaymentStatus | None = None,
        delivery: DeliveryStatus | None = None,
        acceptance: AcceptanceStatus | None = None,
    ) -> None:
        """Update orthogonal process data without altering issued content."""
        if self.lifecycle is LifecycleState.DRAFT:
            raise InvalidLifecycleTransition(
                "Operational statuses are updated after finalization."
            )
        if payment is not None:
            if not document_type_config(self.document_type).payment_applicable:
                if payment is not PaymentStatus.NOT_APPLICABLE:
                    raise DocumentInvariantViolation(
                        "Payment status does not apply to this document type."
                    )
            self._payment_status = payment
        if delivery is not None:
            self._delivery_status = delivery
        if acceptance is not None:
            self._acceptance_status = acceptance
        self._metadata = replace(self._metadata, updated_at=datetime.now(UTC))

    def copy_as_draft(self) -> Document:
        """Create a new independent, unnumbered draft from current content."""
        copied = Document.create(
            self.document_type, document_date=self.document_date,
            currency=self.currency, seller=self.seller, buyer=self.buyer,
            presentation=self._presentation,
        )
        copied._due_date = self.due_date
        copied._notes = self.notes
        copied._external_order_number = self.external_order_number
        copied._lines = [replace(line, id=uuid4()) for line in self.lines]
        copied._totals = self.totals
        copied._events.clear()
        occurred_at, event_id = event_identity()
        copied._events.append(
            DocumentCopied(copied.id, occurred_at, event_id, self.id)
        )
        return copied

    def collect_events(self) -> tuple[DomainEvent, ...]:
        """Return pending events in order and clear the aggregate outbox."""
        events = tuple(self._events)
        self._events.clear()
        return events
