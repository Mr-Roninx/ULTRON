from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SubscriptionCivilizationEntity(BaseModel):
    subscription_id: str
    customer_id: str
    merchant_id: str
    amount: float
    interval: str = "MONTHLY" # MONTHLY, QUARTERLY, ANNUAL
    status: str = "ACTIVE" # ACTIVE, RENEWAL_DUE, RENEWAL_FAILED, RECOVERY, CANCELLED
    current_period_end: int = 1760000000

class SubscriptionEconomyEngine:
    """
    Manages recurring subscriptions and computes next renewal timestamps.
    """
    @staticmethod
    def get_next_renewal_timestamp(current_timestamp: int, interval: str) -> int:
        seconds_map = {
            "MONTHLY": 30 * 86400,
            "QUARTERLY": 90 * 86400,
            "ANNUAL": 365 * 86400
        }
        return current_timestamp + seconds_map.get(interval.upper(), 30 * 86400)
