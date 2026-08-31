from typing import Dict, Any, List, Optional
from pydantic import Field
from synthetic_payment_universe.world_v12.entities.base import WorldEntity

class Customer(WorldEntity):
    customer_id: str
    tier: str = "SMB" # B2C, SMB, MID_MARKET, B2B_ENTERPRISE
    geography: str = "IN"
    currency: str = "INR"
    lifecycle_state: str = "ACTIVE"
    latent_profile: str = "STANDARD" # Evaluator-only variable
    preferred_channels: List[str] = Field(default_factory=lambda: ["EMAIL", "SMS", "WHATSAPP"])
    payment_preferences: List[str] = Field(default_factory=lambda: ["CARD", "UPI", "BANK_TRANSFER"])
    fatigue_score: float = 0.0 # Observable [0.0, 1.0]
    relationship_state: str = "HEALTHY"
    average_transaction_value: float = 25000.0
    historical_success_rate: float = 0.85
    tenure_days: int = 180
    subscription_count: int = 1
    invoice_count: int = 0
    lifetime_value: float = 300000.0
