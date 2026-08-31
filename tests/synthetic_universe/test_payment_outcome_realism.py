import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator
from synthetic_payment_universe.generator.merchant_gen import MerchantGenerator
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator
from synthetic_payment_universe.validators.statistical_validator import UniverseStatisticalValidator

def test_payment_outcome_distribution_realism():
    mgr = MasterSeedManager(101, partition_name="dev")
    cgen = CustomerGenerator(mgr)
    mgen = MerchantGenerator(mgr)
    pgen = PaymentUniverseGenerator(mgr)

    custs = cgen.generate_batch(50)
    merchs = mgen.generate_batch(10)

    payments = []
    for i, c in enumerate(custs):
        m = merchs[i % len(merchs)]
        pmt, _, _ = pgen.generate_payment_scenario(i, c, m)
        payments.append(pmt)

    is_valid, stats, errs = UniverseStatisticalValidator.validate_distributions(payments)
    assert is_valid is True, f"Statistical validation failed: {errs}"
    assert stats["failure_rate"] < 0.35
    assert stats["success_rate"] > 0.65
    assert "SETTLED" in stats["status_breakdown"]
    assert "FAILED" in stats["status_breakdown"]
