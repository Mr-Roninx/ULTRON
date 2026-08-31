from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity

class PopulationChurnDynamics:
    """
    Evaluates customer churn and reactivation probability.
    """
    @staticmethod
    def calculate_churn_risk(customer: PopulationCustomerEntity) -> float:
        risk = customer.churn_probability
        if customer.fatigue_score > 0.75:
            risk += 0.25
        if customer.relationship_score < 0.35:
            risk += 0.35
        return min(0.99, round(risk, 3))
