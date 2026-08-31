from typing import Dict, Any, List, Optional
from pydantic import Field
from synthetic_payment_universe.world_v12.entities.base import WorldEntity

class PaymentMethod(WorldEntity):
    method_id: str
    customer_id: str
    method_type: str = "CARD" # CARD, UPI, BANK_ACCOUNT, E_MANDATE
    network: str = "VISA"
    issuer: str = "HDFC_BANK"
    expiry: str = "12/28"
    token_status: str = "ACTIVE"
    is_default: bool = True

class Payment(WorldEntity):
    payment_id: str
    customer_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    status: str = "SETTLED" # SETTLED, FAILED, PENDING, REVERSED, DISPUTED
    payment_type: str = "INVOICE" # INVOICE, SUBSCRIPTION, CHECKOUT
    rail: str = "CARD"
    gateway_id: str = "GATEWAY_A"
    failure_code: Optional[str] = None
    failure_reason: Optional[str] = None
    attempt_count: int = 1
    due_at: Optional[int] = None

class PaymentAttempt(WorldEntity):
    attempt_id: str
    payment_id: str
    attempt_number: int = 1
    rail: str = "CARD"
    gateway_id: str = "GATEWAY_A"
    status: str = "SUCCESS" # SUCCESS, FAILED, PENDING
    failure_code: Optional[str] = None
    latency_ms: float = 120.0
    timestamp: int = 1760000000

class Invoice(WorldEntity):
    invoice_id: str
    buyer_id: str
    seller_id: str
    amount: float
    currency: str = "INR"
    due_timestamp: int
    status: str = "OPEN" # OPEN, PAID, OVERDUE, DISPUTED
    po_number: Optional[str] = None
    dispute_id: Optional[str] = None

class Subscription(WorldEntity):
    subscription_id: str
    customer_id: str
    merchant_id: str
    plan_name: str
    interval: str = "MONTHLY"
    amount: float
    currency: str = "INR"
    status: str = "ACTIVE" # ACTIVE, PAST_DUE, CANCELLED
    current_period_end: int = 1760000000 + (30 * 86400)

class Checkout(WorldEntity):
    checkout_id: str
    customer_id: str
    merchant_id: str
    cart_total: float
    status: str = "COMPLETED" # COMPLETED, ABANDONED

class Dispute(WorldEntity):
    dispute_id: str
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    dispute_type: str # MISSING_PO, LINE_ITEM_MISMATCH, FRAUD_CLAIM
    status: str = "OPEN" # OPEN, RESOLVED, REJECTED
    requires_human_intervention: bool = True
