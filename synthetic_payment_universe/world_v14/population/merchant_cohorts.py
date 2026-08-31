from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class MerchantCohort(str, Enum):
    GROWING_TECH = "GROWING_TECH"
    STABLE_RETAIL = "STABLE_RETAIL"
    SEASONAL_HOSPITALITY = "SEASONAL_HOSPITALITY"
    STRESSED_LOGISTICS = "STRESSED_LOGISTICS"
    ENTERPRISE_B2B = "ENTERPRISE_B2B"

class MerchantLifecycleState(str, Enum):
    NEW = "NEW"
    GROWING = "GROWING"
    STABLE = "STABLE"
    STRESSED = "STRESSED"
    DECLINING = "DECLINING"
    CHURNED = "CHURNED"

class PopulationMerchantEntity(BaseModel):
    merchant_id: str
    cohort: MerchantCohort = MerchantCohort.STABLE_RETAIL
    industry: str = "SaaS"
    monthly_volume: float = 10000000.0
    growth_rate: float = 0.03 # Monthly volume growth rate
    lifecycle_state: MerchantLifecycleState = MerchantLifecycleState.STABLE
    primary_gateway_id: str = "GATEWAY_A"
    secondary_gateway_id: str = "GATEWAY_B"
    outstanding_receivables: float = 0.0
    recovered_revenue: float = 0.0
    active_customers: int = 500
