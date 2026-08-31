import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator
from synthetic_payment_universe.generator.merchant_gen import MerchantGenerator
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator
from synthetic_payment_universe.counterfactual.counterfactual_engine import UniverseCounterfactualEngine
from synthetic_payment_universe.validators.counterfactual_validator import UniverseCounterfactualValidator

def test_counterfactual_integrity_across_branches():
    mgr = MasterSeedManager(606, partition_name="evaluation")
    cgen = CustomerGenerator(mgr)
    mgen = MerchantGenerator(mgr)
    pgen = PaymentUniverseGenerator(mgr)
    cf_engine = UniverseCounterfactualEngine(mgr)

    cust = cgen.generate_customer(1)
    merch = mgen.generate_merchant(1)
    pmt, _, truth = pgen.generate_payment_scenario(1, cust, merch)

    branches = cf_engine.evaluate_counterfactual_branches(
        decision_point_id="dp_integ_test",
        payment=pmt,
        customer=cust,
        ground_truth=truth
    )

    is_valid, errs = UniverseCounterfactualValidator.validate_counterfactual_set(branches)
    assert is_valid is True, f"Counterfactual validator failed: {errs}"
    assert len(branches) == 5
    for b in branches:
        assert b.payment_id == pmt.payment_id
        assert b.customer_id == cust.customer_id
