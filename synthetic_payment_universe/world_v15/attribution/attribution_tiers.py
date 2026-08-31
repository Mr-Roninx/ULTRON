from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel

class EconomicAttributionTier(str, Enum):
    DIRECT_INCREMENTAL_REVENUE = "DIRECT_INCREMENTAL_REVENUE"
    PROBABLE_INCREMENTAL_REVENUE = "PROBABLE_INCREMENTAL_REVENUE"
    DOWNSTREAM_INCREMENTAL_REVENUE = "DOWNSTREAM_INCREMENTAL_REVENUE"
    NON_INCREMENTAL_RECOVERY = "NON_INCREMENTAL_RECOVERY"
    NEGATIVE_EXTERNALITY = "NEGATIVE_EXTERNALITY"

class MultiTierEconomicAttribution(BaseModel):
    direct_incremental_revenue: float = 0.0
    probable_incremental_revenue: float = 0.0
    downstream_incremental_revenue: float = 0.0
    non_incremental_recovery: float = 0.0
    negative_externality: float = 0.0
    operational_cost: float = 0.0
    net_economic_value: float = 0.0

class MultiTierAttributionEngine:
    """
    Classifies monetary recovery into rigorous attribution tiers.
    """
    @staticmethod
    def classify_attribution(
        recovered_amount: float,
        is_natural_recovery: bool,
        forward_ltv_delta: float,
        externality_cost: float,
        operational_cost: float
    ) -> MultiTierEconomicAttribution:
        direct_inc = 0.0
        non_inc = 0.0

        if is_natural_recovery:
            # Paid anyway -> non-incremental
            non_inc = recovered_amount
        else:
            # Truly saved by agent
            direct_inc = recovered_amount

        downstream = max(0.0, forward_ltv_delta)
        net_nev = round(direct_inc + downstream - externality_cost - operational_cost, 2)

        return MultiTierEconomicAttribution(
            direct_incremental_revenue=round(direct_inc, 2),
            probable_incremental_revenue=0.0,
            downstream_incremental_revenue=round(downstream, 2),
            non_incremental_recovery=round(non_inc, 2),
            negative_externality=round(externality_cost, 2),
            operational_cost=round(operational_cost, 2),
            net_economic_value=net_nev
        )
