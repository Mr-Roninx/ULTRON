from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity, CustomerLifecycleState
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity, MerchantLifecycleState

class PopulationLifecycleEngine:
    """
    Simulates emergent lifecycle transitions for customers and merchants based on economic experiences.
    """
    @staticmethod
    def evaluate_customer_lifecycle(customer: PopulationCustomerEntity, days_since_last_purchase: float):
        if customer.lifecycle_state == CustomerLifecycleState.CHURNED:
            return

        if customer.churn_probability > 0.70 or customer.fatigue_score > 0.85:
            customer.lifecycle_state = CustomerLifecycleState.CHURNED
        elif days_since_last_purchase > 60:
            customer.lifecycle_state = CustomerLifecycleState.DORMANT
        elif days_since_last_purchase > 30 or customer.relationship_score < 0.40:
            customer.lifecycle_state = CustomerLifecycleState.AT_RISK
        else:
            customer.lifecycle_state = CustomerLifecycleState.ACTIVE

    @staticmethod
    def evaluate_merchant_lifecycle(merchant: PopulationMerchantEntity):
        if merchant.outstanding_receivables > (merchant.monthly_volume * 0.40):
            merchant.lifecycle_state = MerchantLifecycleState.STRESSED
        elif merchant.growth_rate > 0.05:
            merchant.lifecycle_state = MerchantLifecycleState.GROWING
        elif merchant.growth_rate < -0.05:
            merchant.lifecycle_state = MerchantLifecycleState.DECLINING
        else:
            merchant.lifecycle_state = MerchantLifecycleState.STABLE
