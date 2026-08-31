import pytest
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity, CustomerCohort
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity
from synthetic_payment_universe.world_v14.economy.emergent_demand import EmergentPaymentDemandEngine

def test_emergent_payment_demand():
    cust = PopulationCustomerEntity(customer_id="c_d1", cohort=CustomerCohort.HIGHLY_LOYAL, spending_capacity=20000.0)
    merch = PopulationMerchantEntity(merchant_id="m_d1")

    # High trust creates positive purchase demand
    amt = EmergentPaymentDemandEngine.evaluate_purchase_intent(cust, merch, relationship_trust=0.95, subseed=1)
    assert amt is not None
    assert 15000.0 <= amt <= 25000.0
