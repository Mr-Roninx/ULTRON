import pytest
from synthetic_payment_universe.world_v12.entities.payment import Payment
from synthetic_payment_universe.world_v12.entities.customer import Customer
from synthetic_payment_universe.world_v12.counterfactual.counterfactual_fork import WorldCounterfactualForkEngine

def test_counterfactual_common_random_numbers_fairness():
    e1 = WorldCounterfactualForkEngine(master_seed=555)
    e2 = WorldCounterfactualForkEngine(master_seed=555)

    cust = Customer(customer_id="c_crn", tier="MID_MARKET")
    pmt = Payment(payment_id="p_crn_0001", customer_id="c_crn", merchant_id="m_1", amount=50000.0)

    out1 = e1.evaluate_branches("dp_crn", pmt, cust, natural_recovery=True)
    out2 = e2.evaluate_branches("dp_crn", pmt, cust, natural_recovery=True)

    for o1, o2 in zip(out1, out2):
        assert o1.net_economic_value == o2.net_economic_value
        assert o1.success == o2.success
