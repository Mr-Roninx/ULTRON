from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CustomerEconomicState(str, Enum):
    ACTIVE = "ACTIVE"
    ENGAGED = "ENGAGED"
    LOW_ENGAGEMENT = "LOW_ENGAGEMENT"
    LIQUID = "LIQUID"
    TEMPORARILY_ILLIQUID = "TEMPORARILY_ILLIQUID"
    CASHFLOW_STRESSED = "CASHFLOW_STRESSED"
    HIGH_FATIGUE = "HIGH_FATIGUE"
    AT_RISK = "AT_RISK"
    CHURNING = "CHURNING"
    CHURNED = "CHURNED"
    RECOVERED = "RECOVERED"

class CustomerEconomyEntity(BaseModel):
    customer_id: str
    tier: str = "SMB" # B2C, SMB, MID_MARKET, B2B_ENTERPRISE
    state: CustomerEconomicState = CustomerEconomicState.ACTIVE
    fatigue_score: float = 0.0 # [0.0, 1.0]
    relationship_score: float = 0.90 # [0.0, 1.0]
    churn_probability: float = 0.05
    lifetime_value: float = 150000.0
    average_transaction_value: float = 15000.0
    historical_success_rate: float = 0.85
    created_at: int = 1760000000
    last_payment_timestamp: Optional[int] = None
    last_contact_timestamp: Optional[int] = None

class CustomerEconomyEngine:
    """
    Manages customer economic states, dynamic fatigue decay, and relationship transitions.
    """
    @staticmethod
    def apply_contact(customer: CustomerEconomyEntity, channel: str, timestamp: int):
        deltas = {
            "EMAIL": 0.05,
            "SMS": 0.08,
            "WHATSAPP": 0.12,
            "VOICE": 0.25,
            "HUMAN_ESCALATION": 0.02
        }
        delta = deltas.get(channel.upper(), 0.08)
        customer.fatigue_score = min(1.0, round(customer.fatigue_score + delta, 3))
        customer.last_contact_timestamp = timestamp
        if customer.fatigue_score > 0.70:
            customer.state = CustomerEconomicState.HIGH_FATIGUE

    @staticmethod
    def decay_fatigue(customer: CustomerEconomyEntity, days_passed: float):
        # Fatigue decays exponentially over time (half-life ~ 5 days)
        decay_factor = 0.85 ** days_passed
        customer.fatigue_score = max(0.0, round(customer.fatigue_score * decay_factor, 3))
        if customer.fatigue_score < 0.40 and customer.state == CustomerEconomicState.HIGH_FATIGUE:
            customer.state = CustomerEconomicState.ACTIVE

    @staticmethod
    def record_successful_recovery(customer: CustomerEconomyEntity, amount: float, timestamp: int):
        customer.state = CustomerEconomicState.RECOVERED
        customer.relationship_score = min(1.0, round(customer.relationship_score + 0.05, 3))
        customer.churn_probability = max(0.01, round(customer.churn_probability * 0.80, 3))
        customer.lifetime_value = round(customer.lifetime_value + amount, 2)
        customer.last_payment_timestamp = timestamp
