from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class Customer(BaseModel):
    id: str
    name: str
    segment: str
    ltv: float = 0.0
    created_at: int
    recent_contacts: int = 0
    recent_responses: int = 0
    successful_prior_recoveries: int = 0
    complaints: int = 0
    opt_out: bool = False
    silence_duration: int = 0

class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    INITIATED = "INITIATED"
    AUTHORIZING = "AUTHORIZING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    RECONCILING = "RECONCILING"
    REVERSED = "REVERSED"
    REFUNDED = "REFUNDED"

class Payment(BaseModel):
    id: str
    customer_id: str
    amount: float
    status: PaymentStatus = PaymentStatus.CREATED
    failure_code: Optional[str] = None
    rail: Optional[str] = None
    gateway_id: Optional[str] = None
    created_at: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaymentAttempt(BaseModel):
    id: str
    payment_id: str
    gateway_id: str
    status: PaymentStatus
    failure_code: Optional[str] = None
    timestamp: int

class InvoiceStatus(str, Enum):
    CREATED = "CREATED"
    OVERDUE = "OVERDUE"
    PAID = "PAID"

class Invoice(BaseModel):
    id: str
    customer_id: str
    amount: float
    status: InvoiceStatus = InvoiceStatus.CREATED
    due_date: int
    created_at: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CheckoutStatus(str, Enum):
    STARTED = "STARTED"
    ABANDONED = "ABANDONED"
    COMPLETED = "COMPLETED"

class Checkout(BaseModel):
    id: str
    customer_id: str
    amount: float
    status: CheckoutStatus = CheckoutStatus.STARTED
    created_at: int

class Gateway(BaseModel):
    id: str
    name: str
    health: float = 1.0
    supported_rails: List[str] = []
    failure_rate: float = 0.0

class RecoveryAction(BaseModel):
    id: str
    mission_id: str
    customer_id: str
    action_type: str
    status: str
    expected_value: float
    observed_value: Optional[float] = None
    timestamp: int

class Communication(BaseModel):
    id: str
    customer_id: str
    channel: str
    message_type: str
    sent_at: int
    response: Optional[str] = None

class MissionGoal(BaseModel):
    type: str
    target: float

class MissionConstraints(BaseModel):
    max_contacts: int
    max_discount: float
    max_risk: float

class MissionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"

class Mission(BaseModel):
    mission_id: str
    objective: str
    starting_state: dict
    observations: List[dict] = []
    hypotheses: List[str] = []
    plans: List[dict] = []
    actions: List[dict] = []
    results: List[dict] = []
    prediction_errors: List[dict] = []
    replans: List[dict] = []
    final_outcome: Optional[dict] = None
    goal: MissionGoal
    deadline: int
    constraints: MissionConstraints
    authority: str
    status: MissionStatus = MissionStatus.PENDING
    recovered_amount: float = 0.0
