from enum import Enum
from pydantic import BaseModel

class CustomerSensitivityType(str, Enum):
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"       # Dislikes contact, high fatigue gain (+0.25)
    INTERVENTION_RESISTANT = "INTERVENTION_RESISTANT" # Rarely responds, requires wait or voice
    COMMUNICATION_SEEKING = "COMMUNICATION_SEEKING"   # Converts readily on 1-click link
    NATURAL_RECOVERER = "NATURAL_RECOVERER"     # Retries on own within 6h (85% base p)
    NEUTRAL = "NEUTRAL"

class HeterogeneousCustomerEntity(BaseModel):
    customer_id: str
    tier: str = "SMB"
    sensitivity_type: CustomerSensitivityType = CustomerSensitivityType.NEUTRAL
    spending_capacity: float = 25000.0
    relationship_score: float = 0.90
    fatigue_rolling_24h: float = 0.0
    fatigue_rolling_7d: float = 0.0
    churn_status: str = "ACTIVE"
