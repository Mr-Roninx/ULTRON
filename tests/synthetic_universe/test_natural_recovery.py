import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator
from synthetic_payment_universe.generator.merchant_gen import MerchantGenerator
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator

def test_natural_recovery_trajectory_modeling():
    mgr = MasterSeedManager(202, partition_name="evaluation")
    cgen = CustomerGenerator(mgr)
    mgen = MerchantGenerator(mgr)
    pgen = PaymentUniverseGenerator(mgr)

    cust = cgen.generate_customer(1)
    merch = mgen.generate_merchant(1)

    # Collect ground truths across multiple scenarios
    failed_truths = []
    for i in range(200):
        pmt, _, truth = pgen.generate_payment_scenario(i, cust, merch)
        if pmt.status == "FAILED":
            failed_truths.append(truth)

    assert len(failed_truths) > 0
    # Check that a subset of transient failures naturally recover
    natural_recs = [gt for gt in failed_truths if gt.eventual_payment]
    assert len(natural_recs) > 0
    for nr in natural_recs:
        assert nr.natural_recovery_timestamp is not None
