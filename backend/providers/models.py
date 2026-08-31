from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class CanonicalPaymentState(str, Enum):
    CREATED = "CREATED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    SETTLEMENT_PENDING = "SETTLEMENT_PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"
    RECONCILING = "RECONCILING"

class CanonicalPaymentFailureClass(str, Enum):
    TRANSIENT = "TRANSIENT"
    CUSTOMER_ACTION_REQUIRED = "CUSTOMER_ACTION_REQUIRED"
    HARD_DECLINE = "HARD_DECLINE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    AUTHENTICATION = "AUTHENTICATION"
    LIMIT = "LIMIT"
    CONFIGURATION = "CONFIGURATION"
    AMBIGUOUS = "AMBIGUOUS"
    SETTLEMENT = "SETTLEMENT"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"

class PaymentIdentityMap(BaseModel):
    internal_payment_id: str
    provider: str
    provider_account_id: str
    provider_object_id: str # e.g. pay_xxx, pi_xxx
    merchant_reference: str
    external_reference: Optional[str] = None
    created_at: int

class CanonicalCustomer(BaseModel):
    customer_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: str = "SMB"
    currency: str = "INR"

class CanonicalPayment(BaseModel):
    internal_payment_id: str
    provider: str
    provider_payment_id: str
    order_id: Optional[str] = None
    customer_id: str
    merchant_id: str
    amount_minor: int # Integer minor units: e.g. 2470000 paise = INR 24,700.00
    currency: str = "INR"
    state: CanonicalPaymentState = CanonicalPaymentState.CREATED
    failure_class: Optional[CanonicalPaymentFailureClass] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    method: Optional[str] = None # CARD, UPI, NETBANKING, ACH
    created_at: int
    updated_at: int
    settled_at: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def amount_major(self) -> float:
        return self.amount_minor / 100.0

class CanonicalPaymentLink(BaseModel):
    link_id: str
    internal_payment_id: str
    provider: str
    provider_link_id: str
    short_url: str
    amount_minor: int
    currency: str = "INR"
    status: str # CREATED, PAID, EXPIRED, CANCELLED
    customer_id: str
    created_at: int
    expires_at: Optional[int] = None
    paid_at: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CanonicalPaymentEvent(BaseModel):
    event_id: str
    provider: str
    provider_event_id: str
    event_type: str # e.g. PAYMENT_SUCCEEDED, PAYMENT_FAILED
    internal_payment_id: Optional[str] = None
    provider_payment_id: Optional[str] = None
    timestamp: int
    payload: Dict[str, Any] = Field(default_factory=dict)
    raw_event_type: Optional[str] = None
    signature_verified: bool = False

class CanonicalRefund(BaseModel):
    refund_id: str
    internal_payment_id: str
    provider: str
    provider_refund_id: str
    amount_minor: int
    currency: str = "INR"
    status: str # PENDING, PROCESSED, FAILED
    reason: Optional[str] = None
    created_at: int

class CanonicalSettlement(BaseModel):
    settlement_id: str
    provider: str
    provider_settlement_id: str
    amount_minor: int
    fee_minor: int
    tax_minor: int
    currency: str = "INR"
    status: str # SETTLED, PENDING
    settled_at: int
