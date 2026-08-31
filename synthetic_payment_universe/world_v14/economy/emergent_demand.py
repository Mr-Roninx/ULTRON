import random
from typing import Dict, Any, List, Optional
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity, CustomerLifecycleState
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity

class EmergentPaymentDemandEngine:
    """
    Generates payment demand from interaction of customer cohorts, merchant activity, and relationships.
    """
    @staticmethod
    def evaluate_purchase_intent(
        customer: PopulationCustomerEntity,
        merchant: PopulationMerchantEntity,
        relationship_trust: float,
        macro_surge_mult: float = 1.0,
        subseed: int = 12345
    ) -> Optional[float]:
        if customer.lifecycle_state in [CustomerLifecycleState.CHURNED, CustomerLifecycleState.DORMANT]:
            return None

        rng = random.Random(subseed)
        base_propensity = 0.20
        if customer.cohort == "HIGHLY_LOYAL":
            base_propensity = 0.55
        elif customer.cohort == "PRICE_SENSITIVE":
            base_propensity = 0.15
        elif customer.cohort == "ENTERPRISE_PROCUREMENT":
            base_propensity = 0.30

        # Adjust for relationship trust and macro shocks
        effective_p = min(0.95, base_propensity * relationship_trust * macro_surge_mult)

        if rng.random() < effective_p:
            # Generate emergent transaction amount
            spend = customer.spending_capacity
            amt = round(rng.uniform(spend * 0.75, spend * 1.25), 2)
            return amt
        return None
