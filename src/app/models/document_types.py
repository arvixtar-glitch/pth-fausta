"""Document-domain enumerations and type-specific configuration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DocumentType(StrEnum):
    """Define the supported business-document purposes."""

    INVOICE = "invoice"
    PROFORMA = "proforma"
    COMMERCIAL_OFFER = "commercial_offer"
    EBAY_INVOICE = "ebay_invoice"


class LifecycleState(StrEnum):
    """Define the accounting lifecycle of a document."""

    DRAFT = "draft"
    FINALIZED = "finalized"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    """Define the independent payment process state."""

    NOT_APPLICABLE = "not_applicable"
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"


class DeliveryStatus(StrEnum):
    """Define the independent delivery process state."""

    NOT_SENT = "not_sent"
    SENT = "sent"
    DELIVERED = "delivered"
    DELIVERY_FAILED = "delivery_failed"
    NOT_APPLICABLE = "not_applicable"


class AcceptanceStatus(StrEnum):
    """Define the independent recipient-acceptance state."""

    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PriceBasis(StrEnum):
    """Define whether a unit price excludes or includes VAT."""

    NET = "net"
    GROSS = "gross"


class VatTreatment(StrEnum):
    """Define the legal tax meaning of a document line."""

    STANDARD = "standard"
    ZERO_RATE = "zero_rate"
    EXEMPT = "exempt"
    OUT_OF_SCOPE = "out_of_scope"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class DocumentTypeConfig:
    """Describe explicit behavioural differences between document types."""

    default_series: str
    payment_applicable: bool
    buyer_required: bool
    due_date_required: bool
    default_payment_status: PaymentStatus
    default_acceptance_status: AcceptanceStatus
    external_order_required: bool = False


DOCUMENT_TYPE_CONFIGS: dict[DocumentType, DocumentTypeConfig] = {
    DocumentType.INVOICE: DocumentTypeConfig(
        "SF", True, True, True, PaymentStatus.UNPAID,
        AcceptanceStatus.NOT_APPLICABLE,
    ),
    DocumentType.PROFORMA: DocumentTypeConfig(
        "IS", True, True, True, PaymentStatus.UNPAID,
        AcceptanceStatus.PENDING,
    ),
    DocumentType.COMMERCIAL_OFFER: DocumentTypeConfig(
        "KP", False, True, False, PaymentStatus.NOT_APPLICABLE,
        AcceptanceStatus.PENDING,
    ),
    DocumentType.EBAY_INVOICE: DocumentTypeConfig(
        "EB", True, True, True, PaymentStatus.UNPAID,
        AcceptanceStatus.NOT_APPLICABLE, external_order_required=True,
    ),
}


def document_type_config(document_type: DocumentType) -> DocumentTypeConfig:
    """Return the complete configuration for a supported document type."""
    return DOCUMENT_TYPE_CONFIGS[document_type]
