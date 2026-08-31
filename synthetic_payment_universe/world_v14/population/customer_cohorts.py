from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CustomerCohort(str, Enum):
    SALARY_CYCLE_CONSUMER = "SALARY_CYCLE_CONSUMER"
    VOLATILE_INCOME_SMB = "VOLATILE_INCOME_SMB"
    HIGHLY_LOYAL = "HIGHLY_LOYAL"
    PRICE_SENSITIVE = "PRICE_SENSITIVE"
    SEASONAL_CONSUMER = "SEASONAL_CONSUMER"
    ENTERPRISE_PROCUREMENT = "ENTERPRISE_PROCUREMENT"
    LOW_ENGAGEMENT = "LOW_ENGAGEMENT"

class CustomerLifecycleState(str, Enum):
    PROSPECT = "PROSPECT"
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    DORMANT = "DORMANT"
    CHURNED = "CHURNED"
    REACTIVATED = "REACTIVATED"

class PopulationCustomerEntity(BaseModel):
    customer_id: str
    cohort: CustomerCohort = CustomerCohort.SALARY_CYCLE_CONSUMER
    tier: str = "SMB" # B2C, SMB, MID_MARKET, B2B_ENTERPRISE
    lifecycle_state: CustomerLifecycleState = CustomerLifecycleState.ACTIVE
    spending_capacity: float = 25000.0
    fatigue_score: float = 0.0 # [0.0, 1.0]
    relationship_score: float = 0.90 # [0.0, 1.0]
    churn_probability: float = 0.04
    created_at: int = 1760000000
    last_purchase_timestamp: Optional[int] = None
    last_contact_timestamp: Optional[int] = None
