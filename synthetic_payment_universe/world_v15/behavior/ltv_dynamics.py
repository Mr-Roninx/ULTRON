from typing import Dict, Any
from synthetic_payment_universe.world_v15.behavior.customer_heterogeneity import HeterogeneousCustomerEntity

class CustomerLTVDynamics:
    """
    Evaluates multi-horizon forward customer lifetime value (30d, 90d, 365d) based on relationship trust.
    """
    @staticmethod
    def project_future_revenue(customer: HeterogeneousCustomerEntity, horizon_days: int) -> float:
        if customer.churn_status == "CHURNED":
            return 0.0

        # Frequency: B2C = 4 purchases/mo, SMB = 2/mo, Enterprise = 0.5/mo
        monthly_freq = 2.0 if customer.tier == "SMB" else (4.0 if customer.tier == "B2C" else 0.5)
        months = horizon_days / 30.0

        # Trust scales expected completion rate
        expected_purchases = monthly_freq * months * max(0.05, customer.relationship_score)
        forward_gmv = expected_purchases * customer.spending_capacity

        return round(forward_gmv, 2)
