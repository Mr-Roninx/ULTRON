import pytest
from simulator.clock import clock
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator
from synthetic_payment_universe.generator.merchant_gen import MerchantGenerator
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator

def test_customer_longitudinal_financial_history():
    now = 1760000000
    clock.reset(now)
    mgr = MasterSeedManager(303, partition_name="dev")
    cgen = CustomerGenerator(mgr)
    mgen = MerchantGenerator(mgr)
    pgen = PaymentUniverseGenerator(mgr)

    cust = cgen.generate_customer(1)
    merch = mgen.generate_merchant(1)

    hist = pgen.generate_customer_longitudinal_history(
        customer=cust,
        merchant=merch,
        event_count=8,
        base_index=100
    )

    assert len(hist) == 8
    # Verify strict ascending chronological ordering preceding now
    prev_t = 0
    for p, atts, gt in hist:
        assert p.created_at <= now
        assert p.created_at >= prev_t
        prev_t = p.created_at
