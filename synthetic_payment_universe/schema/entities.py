import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from simulator.clock import clock
from synthetic_payment_universe.schema.visibility import EventVisibility

class BaseUniverseEntity(BaseModel):
    schema_version: str = "1.0"
    created_at: int = Field(default_factory=clock.now)
    updated_at: int = Field(default_factory=clock.now)

class Customer(BaseUniverseEntity):
    customer_id: str
    name: str
    customer_type: str = "B2B_ENTERPRISE" # B2C, SMB, MID_MARKET, ENTERPRISE
    segment: str = "B2B_ENTERPRISE"
    country: str = "IND"
    currency: str = "INR"
    tenure_days: int = 180
    complaints: int = 0
    contact_count: int = 0
    fatigue_score: float = 0.0 # [0.0, 1.0]
    is_opted_out: bool = False
    average_transaction_value: float = 25000.0
    historical_success_rate: float = 0.88
    # Latent (Hidden) Variables
    latent_profile: str = "PATIENT"
    latent_salary_day: int = 1
    latent_churn_risk: float = 0.05

class Merchant(BaseUniverseEntity):
    merchant_id: str
    name: str
    industry: str = "SaaS" # SaaS, E-commerce, Logistics, Healthcare, etc.
    country: str = "IND"
    currency: str = "INR"
    monthly_volume: float = 5000000.0
    average_order_value: float = 15000.0
    subscription_ratio: float = 0.70
    invoice_ratio: float = 0.30
    refund_rate: float = 0.015
    chargeback_rate: float = 0.002
    primary_gateway_id: str = "GATEWAY_A"
    secondary_gateway_id: str = "GATEWAY_B"

class PaymentMethod(BaseUniverseEntity):
    method_id: str
    customer_id: str
    method_type: str # CREDIT_CARD, DEBIT_CARD, UPI, UPI_AUTOPAY, ACH, E_NACH, BANK_TRANSFER, PAYMENT_LINK
    is_default: bool = True
    is_valid: bool = True
    expiration_timestamp: Optional[int] = None

class Rail(BaseUniverseEntity):
    rail_id: str # CARD, UPI, ACH, E_NACH, BANK_TRANSFER
    name: str
    current_health: float = 0.95
    base_latency_ms: float = 120.0
    is_active: bool = True

class Gateway(BaseUniverseEntity):
    gateway_id: str # GATEWAY_A, GATEWAY_B, GATEWAY_C, GATEWAY_D
    name: str
    current_health: float = 0.95
    latency_ms: float = 150.0
    status: str = "STABLE" # STABLE, DEGRADING, RECOVERING, FLAPPING, OUTAGE, LATENCY_SPIKE, MAINTENANCE

class Payment(BaseUniverseEntity):
    payment_id: str
    customer_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    status: str = "FAILED" # PENDING, FAILED, RECOVERED, SETTLED, DISPUTED, ABANDONED
    rail: str = "CARD"
    gateway_id: str = "GATEWAY_A"
    failure_code: Optional[str] = "91"
    failure_reason: Optional[str] = None
    attempt_count: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaymentAttempt(BaseUniverseEntity):
    attempt_id: str
    payment_id: str
    attempt_number: int
    rail: str
    gateway_id: str
    status: str # SUCCESS, FAILED
    failure_code: Optional[str] = None
    latency_ms: float = 150.0
    timestamp: int = Field(default_factory=clock.now)

class PaymentEvent(BaseUniverseEntity):
    event_id: str
    event_type: str
    payment_id: str
    timestamp: int
    payload: Dict[str, Any]
    visibility: EventVisibility = EventVisibility.OBSERVABLE

class GatewayEvent(BaseUniverseEntity):
    event_id: str
    gateway_id: str
    previous_health: float
    new_health: float
    event_type: str
    timestamp: int
    visibility: EventVisibility = EventVisibility.OBSERVABLE

class CustomerEvent(BaseUniverseEntity):
    event_id: str
    customer_id: str
    event_type: str # CONTACT_RECEIVED, PAYMENT_LINK_OPENED, PTP_PROMISED, OPT_OUT, DISPUTE_OPENED
    timestamp: int
    visibility: EventVisibility = EventVisibility.OBSERVABLE

class Checkout(BaseUniverseEntity):
    checkout_id: str
    customer_id: str
    merchant_id: str
    amount: float
    status: str = "COMPLETED" # STARTED, METHOD_SELECTED, OTP_SENT, 3DS_VERIFIED, ABANDONED, COMPLETED
    abandonment_stage: Optional[str] = None

class Subscription(BaseUniverseEntity):
    subscription_id: str
    customer_id: str
    merchant_id: str
    amount: float
    billing_cycle: str = "MONTHLY"
    next_billing_timestamp: int
    status: str = "ACTIVE" # ACTIVE, PAST_DUE, PAUSED, CANCELLED

class InvoiceLineItem(BaseModel):
    item_id: str
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseUniverseEntity):
    invoice_id: str
    buyer_id: str
    seller_id: str
    amount: float
    currency: str = "INR"
    due_timestamp: int
    status: str = "OPEN" # OPEN, DUE, OVERDUE, DISPUTED, PARTIALLY_PAID, PAID, ESCALATED
    po_number: Optional[str] = None
    dispute_id: Optional[str] = None
    line_items: List[InvoiceLineItem] = Field(default_factory=list)

class Dispute(BaseUniverseEntity):
    dispute_id: str
    invoice_id: str
    dispute_type: str # MISSING_PO, WRONG_PO, LINE_ITEM_MISMATCH, TAX_MISMATCH, CONTRACT_MISMATCH
    status: str = "OPEN" # OPEN, UNDER_REVIEW, RESOLVED_AUTO, RESOLVED_HUMAN, REJECTED
    requires_human_intervention: bool = False

class Communication(BaseUniverseEntity):
    communication_id: str
    customer_id: str
    channel: str # EMAIL, SMS, WHATSAPP, VOICE, IN_APP
    template: str
    status: str = "SENT" # SENT, DELIVERED, OPENED, IGNORED, REPLIED
    sent_timestamp: int
    response_timestamp: Optional[int] = None

class RecoveryAction(BaseUniverseEntity):
    action_id: str
    payment_id: str
    customer_id: str
    action_type: str # WAIT, RETRY_GATEWAY_A, RETRY_GATEWAY_B, SEND_PAYMENT_LINK, APPLY_DISCOUNT, ESCALATE, STOP
    scheduled_timestamp: int
    executed_timestamp: Optional[int] = None
    status: str = "PENDING" # PENDING, EXECUTED, CANCELLED, REJECTED_BY_GUARD

class RecoveryOutcome(BaseUniverseEntity):
    outcome_id: str
    action_id: str
    payment_id: str
    recovered_amount: float
    operational_cost: float
    relationship_cost: float
    net_economic_value: float
    timestamp: int
    success: bool

class Settlement(BaseUniverseEntity):
    settlement_id: str
    payment_id: str
    amount: float
    fee: float
    net_amount: float
    status: str = "SETTLED"
    clearing_timestamp: int

class WebhookEvent(BaseUniverseEntity):
    webhook_id: str
    event_type: str
    idempotency_key: str
    payload: Dict[str, Any]
    dispatch_timestamp: int
    received_timestamp: Optional[int] = None
    status: str = "DELIVERED" # DELIVERED, DELAYED, DROPPED, DUPLICATE

class Episode(BaseUniverseEntity):
    episode_id: str
    customer_id: str
    payment_id: str
    initial_failure_code: str
    final_outcome: str
    total_actions: int
    recovered_amount: float
    net_economic_value: float
    duration_seconds: int

class Observation(BaseUniverseEntity):
    observation_id: str
    customer_id: str
    payment_id: str
    timestamp: int
    context_snapshot: Dict[str, Any]

class GroundTruthOutcome(BaseUniverseEntity):
    truth_id: str
    payment_id: str
    true_root_cause: str
    eventual_payment: bool
    eventual_recovery_amount: float
    natural_recovery_timestamp: Optional[int] = None
    oracle_optimal_action: str
    visibility: EventVisibility = EventVisibility.EVALUATOR_ONLY

class ChaosEvent(BaseUniverseEntity):
    chaos_id: str
    target_entity: str
    perturbation_type: str # GATEWAY_DEGRADATION, WEBHOOK_DELAY, CUSTOMER_DELAY, RAIL_OUTAGE
    scheduled_timestamp: int
    duration_seconds: int
    parameters: Dict[str, Any]
    applied: bool = False

class AuditEvent(BaseUniverseEntity):
    audit_id: str
    actor: str
    action: str
    timestamp: int
    payload_hash: str
