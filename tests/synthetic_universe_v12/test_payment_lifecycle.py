import pytest
from synthetic_payment_universe.world_v12.entities.payment import Payment
from synthetic_payment_universe.world_v12.entities.ledger import SimulatedDoubleEntryLedger
from synthetic_payment_universe.world_v12.payments.processor import SimulatedPaymentProcessor

def test_payment_authorization_lifecycle():
    ledger = SimulatedDoubleEntryLedger()
    processor = SimulatedPaymentProcessor(ledger)

    pmt = Payment(payment_id="p_proc_1", customer_id="c_1", merchant_id="m_1", amount=25000.0, gateway_id="GATEWAY_A")

    # High gateway health -> Success
    attempt, success = processor.process_payment_attempt(pmt, gateway_health=0.99, rail="CARD", timestamp=1760000000, subseed=1)
    assert success is True
    assert pmt.status == "SETTLED"
    assert ledger.verify_ledger_balance() is True
