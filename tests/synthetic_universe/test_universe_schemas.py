import pytest
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Customer, Merchant, Payment, GroundTruthOutcome

def test_universe_entity_creation():
    clock.reset(1760000000)
    cust = Customer(customer_id="c_test_1", name="Test Corp", segment="B2B_ENTERPRISE")
    assert cust.customer_id == "c_test_1"
    assert cust.schema_version == "1.0"
    assert cust.created_at == 1760000000

    merch = Merchant(merchant_id="m_test_1", name="SaaS Merchant", industry="SaaS")
    assert merch.industry == "SaaS"

    pmt = Payment(payment_id="p_test_1", customer_id=cust.customer_id, merchant_id=merch.merchant_id, amount=24700.0)
    assert pmt.amount == 24700.0
