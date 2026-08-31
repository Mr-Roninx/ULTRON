from typing import Dict, Any, List, Optional
from pydantic import Field
from synthetic_payment_universe.world_v12.entities.base import WorldEntity

class Merchant(WorldEntity):
    merchant_id: str
    name: str = "Merchant Corp"
    industry: str = "SaaS" # SaaS, E-commerce, Logistics, Healthcare, Manufacturing, etc.
    size: str = "MID_MARKET"
    risk_profile: str = "LOW"
    currency: str = "INR"
    primary_gateway_id: str = "GATEWAY_A"
    secondary_gateway_id: str = "GATEWAY_B"
    subscription_ratio: float = 0.60
    invoice_ratio: float = 0.40
    monthly_volume: float = 5000000.0
    average_order_value: float = 25000.0
    settlement_delay_days: int = 2
