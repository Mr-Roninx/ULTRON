import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.counterfactual.counterfactual_engine import UniverseCounterfactualEngine
from synthetic_payment_universe.schema.entities import Customer, Payment, GroundTruthOutcome

def test_common_random_numbers_reproducibility():
    mgr1 = MasterSeedManager(777)
    mgr2 = MasterSeedManager(777)

    eng1 = UniverseCounterfactualEngine(mgr1)
    eng2 = UniverseCounterfactualEngine(mgr2)

    cust = Customer(customer_id="c_crn_1", name="CRN Corp")
    pmt = Payment(payment_id="p_crn_1", customer_id="c_crn_1", merchant_id="m_1", amount=15000.0)
    truth = GroundTruthOutcome(truth_id="gt_1", payment_id="p_crn_1", true_root_cause="OUTAGE", eventual_payment=False, eventual_recovery_amount=0.0, oracle_optimal_action="RETRY")

    out1 = eng1.evaluate_counterfactual_branches("dp_1", pmt, cust, truth)
    out2 = eng2.evaluate_counterfactual_branches("dp_1", pmt, cust, truth)

    # All branches must match exactly across identical random number runs
    for o1, o2 in zip(out1, out2):
        assert o1.action_type == o2.action_type
        assert o1.recovered_amount == o2.recovered_amount
        assert o1.net_economic_value == o2.net_economic_value
