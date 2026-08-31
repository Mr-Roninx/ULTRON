import math
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from simulator.clock import clock

ALLOWED_SIGNAL_TYPES = {
    "failure_is_transient",
    "customer_liquidity_likelihood",
    "customer_fatigue_signal",
    "settlement_ambiguity",
    "gateway_instability_signal",
    "alternate_rail_relevance",
    "relationship_risk_signal",
    "urgency_signal"
}

PROHIBITED_ECONOMIC_FIELDS = {
    "nev",
    "expected_recovery",
    "financial_cost",
    "discount_amount",
    "risk_budget",
    "ledger_mutation",
    "payment_amount",
    "balance",
    "sql"
}

class SemanticSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:8]}")
    signal_type: str
    value: float
    confidence: float
    evidence_reference: str
    observed_timestamp: int
    source: str = "LLM_SEMANTIC_REASONER"
    uncertainty: float = 0.0
    calibration_status: str = "RAW"

    @field_validator("signal_type")
    @classmethod
    def validate_signal_type(cls, v: str) -> str:
        if v not in ALLOWED_SIGNAL_TYPES:
            raise ValueError(f"Unauthorized semantic signal type '{v}'. Allowed: {ALLOWED_SIGNAL_TYPES}")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Signal value cannot be NaN or Infinity.")
        if v < 0.0 or v > 1.0:
            raise ValueError(f"Signal value must be bounded in [0.0, 1.0], got {v}")
        return round(float(v), 4)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Confidence cannot be NaN or Infinity.")
        if v < 0.0 or v > 1.0:
            raise ValueError(f"Confidence must be bounded in [0.0, 1.0], got {v}")
        return round(float(v), 4)

    @field_validator("observed_timestamp")
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        now = clock.now()
        if v > now:
            raise ValueError(f"Future timestamp violation: signal timestamp {v} > simulation clock {now}")
        return v

def filter_unauthorized_llm_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strips and rejects any unauthorized financial/economic keys proposed directly by an LLM.
    Ensures the LLM cannot set monetary values, NEV, or ledger mutations.
    """
    sanitized: Dict[str, Any] = {}
    for k, v in payload.items():
        k_lower = k.lower()
        if k_lower in PROHIBITED_ECONOMIC_FIELDS or any(p in k_lower for p in ["money", "balance", "discount_amt", "override_nev"]):
            continue
        sanitized[k] = v
    return sanitized
