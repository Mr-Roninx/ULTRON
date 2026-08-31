from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional
import uuid
from enum import Enum

class ActionScore(BaseModel):
    action: str
    expected_recovery: float
    financial_cost: float
    relationship_cost: float
    operational_cost: float
    risk_cost: float
    nev: float

class PlanStatus(str, Enum):
    PROPOSED = "PROPOSED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    INVALIDATED = "INVALIDATED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"

class WakeReason(str, Enum):
    WAITING_FOR_RETRY = "WAITING_FOR_RETRY"
    WAITING_FOR_CUSTOMER = "WAITING_FOR_CUSTOMER"
    WAITING_FOR_PAYMENT = "WAITING_FOR_PAYMENT"
    WAITING_FOR_GATEWAY = "WAITING_FOR_GATEWAY"
    WAITING_FOR_PTP = "WAITING_FOR_PTP"
    NONE = "NONE"

class Plan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"pln_{uuid.uuid4().hex[:8]}")
    plan_version: int = 1
    created_at: int
    expires_at: Optional[int] = None
    status: PlanStatus = PlanStatus.PROPOSED
    candidate_actions: List[ActionScore] = Field(default_factory=list)
    selected_action: str
    expected_value: float = 0.0
    risk: float = 0.0
    authority: str = "AUTONOMOUS"
    feasibility: bool = True

class AgentIntent(BaseModel):
    mission_id: Optional[str] = None
    customer_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    diagnosis: Optional[str] = None
    observed_facts: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    candidate_actions: List[str] = Field(default_factory=list)
    preferred_action: Optional[str] = None
    rationale: Optional[str] = None
    confidence: float = 0.0
    memory_reference_ids: List[str] = Field(default_factory=list)
    interference_reference_ids: List[str] = Field(default_factory=list)
    requested_tools: List[str] = Field(default_factory=list)

    # Legacy fields (required for deterministic fallbacks and Phase 11 compatibility)
    action_type: str
    reasoning: str
    expected_yield: float
    payload: Dict[str, Any]

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v):
        valid_actions = [
            "WAIT",
            "RECONCILE",
            "RETRY",
            "RETRY_GATEWAY_A",
            "RETRY_GATEWAY_B",
            "RETRY_GATEWAY_C",
            "SWITCH_PERMITTED_RAIL",
            "ALTERNATE_RAIL",
            "REQUEST_CUSTOMER_ACTION",
            "SEND_PAYMENT_LINK",
            "SEND_MESSAGE",
            "EMAIL",
            "SMS",
            "PTP",
            "REGISTER_PTP",
            "APPLY_DISCOUNT",
            "REFUND_PAYMENT",
            "ESCALATE",
            "STOP"
        ]
        if v not in valid_actions:
            raise ValueError(f"Invalid action type: {v}")
        return v
