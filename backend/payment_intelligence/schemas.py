from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class FailureClass(str, Enum):
    LIQUIDITY = "LIQUIDITY"
    CREDENTIAL = "CREDENTIAL"
    ACCOUNT = "ACCOUNT"
    AUTHENTICATION = "AUTHENTICATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GATEWAY = "GATEWAY"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"

class FailureSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RailType(str, Enum):
    CARD = "CARD"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    ACH = "ACH"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"

class RailHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"

class CustomerResponseCode(str, Enum):
    PAY_NOW = "PAY_NOW"
    ASKS_FOR_TIME = "ASKS_FOR_TIME"
    PAYMENT_METHOD_PROBLEM = "PAYMENT_METHOD_PROBLEM"
    DISPUTE = "DISPUTE"
    NO_RESPONSE = "NO_RESPONSE"
    REQUEST_HUMAN = "REQUEST_HUMAN"
    OPTOUT = "OPTOUT"

class PaymentFailureRaw(BaseModel):
    gateway_id: str
    raw_code: str
    amount: float
    rail: str = "CARD"
    raw_message: Optional[str] = None
    currency: str = "INR"
    timestamp: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NormalizedFailure(BaseModel):
    failure_class: FailureClass
    failure_reason: str
    severity: FailureSeverity
    recoverability: float = Field(ge=0.0, le=1.0)
    customer_action_required: bool
    retry_eligible: bool
    typical_recovery_actions: List[str] = Field(default_factory=list)
    prohibited_actions: List[str] = Field(default_factory=list)
    recommended_investigation: List[str] = Field(default_factory=list)
    raw_code: str
    gateway_id: str

class PaymentDiagnosis(BaseModel):
    payment_id: str
    customer_id: str
    primary_reason: str
    failure_class: FailureClass
    severity: FailureSeverity
    recoverability: float = Field(ge=0.0, le=1.0)
    customer_action_required: bool
    retry_eligible: bool
    recommended_investigation: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    suggested_actions: List[str] = Field(default_factory=list)
    prohibited_actions: List[str] = Field(default_factory=list)
    diagnosed_at: int = 0

class GatewayHealthState(BaseModel):
    gateway_id: str
    status: RailHealthStatus = RailHealthStatus.HEALTHY
    success_probability: float = Field(default=0.95, ge=0.0, le=1.0)
    failure_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    timeout_rate: float = Field(default=0.01, ge=0.0, le=1.0)
    latency_ms: float = 250.0
    recovery_trend: float = 0.0 # positive = recovering, negative = degrading
    last_updated: int = 0

class RailHealthState(BaseModel):
    rail: RailType
    status: RailHealthStatus = RailHealthStatus.HEALTHY
    success_probability: float = Field(default=0.92, ge=0.0, le=1.0)
    failure_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    timeout_rate: float = Field(default=0.02, ge=0.0, le=1.0)
    latency_ms: float = 400.0
    active_gateways: List[str] = Field(default_factory=list)
    last_updated: int = 0
