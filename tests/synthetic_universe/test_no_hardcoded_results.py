import pytest
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.schema.entities import Customer, Merchant

def test_no_hardcoded_outcomes_in_generation():
    mgr = MasterSeedManager(42)
    pgen = PaymentUniverseGenerator(mgr)
    cust = Customer(customer_id="c_1", name="Corp 1")
    merch = Merchant(merchant_id="m_1", name="Merch 1")

    pmt, attempts, truth = pgen.generate_payment_scenario(1, cust, merch)
    raw_dict = pmt.model_dump()

    # Verify no fabricated evaluation outcome fields
    assert "ultron_success" not in raw_dict
    assert "ultron_recovery" not in raw_dict
    assert "llm_improvement" not in raw_dict
