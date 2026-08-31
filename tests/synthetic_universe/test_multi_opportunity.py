import pytest
from synthetic_payment_universe.interference.cross_opportunity import interference_engine
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator
from synthetic_payment_universe.generator.merchant_gen import MerchantGenerator
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator

def test_multi_opportunity_customer_interference():
    interference_engine.reset()
    mgr = MasterSeedManager(404, partition_name="dev")
    cgen = CustomerGenerator(mgr)
    mgen = MerchantGenerator(mgr)
    pgen = PaymentUniverseGenerator(mgr)

    cust = cgen.generate_customer(1)
    merch = mgen.generate_merchant(1)

    # Generate payment + B2B invoice
    pmt, _, _ = pgen.generate_payment_scenario(1, cust, merch)
    inv, disp = pgen.generate_b2b_invoice_with_dispute(1, cust, merch)

    interference_engine.register_opportunity(cust.customer_id, "PAYMENT", pmt.amount, pmt.payment_id)
    interference_engine.register_opportunity(cust.customer_id, "INVOICE", inv.amount, inv.invoice_id)

    summary = interference_engine.get_customer_summary(cust.customer_id)
    assert len(summary["opportunities"]) == 2
    assert summary["total_amount"] == pmt.amount + inv.amount

    # Action triggers cross-opportunity fatigue penalty
    mult = interference_engine.apply_cross_action_interference(cust.customer_id, "SEND_PAYMENT_LINK")
    assert mult > 1.0
