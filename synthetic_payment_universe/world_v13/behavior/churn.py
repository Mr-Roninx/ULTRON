from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity, CustomerEconomicState

class ChurnModel:
    """
    Computes churn probability based on relationship score, fatigue, and failed recovery experiences.
    """
    @staticmethod
    def evaluate_churn_risk(customer: CustomerEconomyEntity) -> float:
        base = customer.churn_probability
        if customer.fatigue_score > 0.80:
            base += 0.30
        if customer.relationship_score < 0.40:
            base += 0.40
        return min(0.99, round(base, 3))
