import pytest
from synthetic_payment_universe.world_v13.economy.payment_economy import PaymentCivilizationEntity, PaymentEconomyEngine

def test_payment_authorization_lifecycle():
    pmt = PaymentCivilizationEntity(payment_id="p_test_1", customer_id="c_1", merchant_id="m_1", amount=25000.0)
    success, fcode = PaymentEconomyEngine.process_authorization(pmt, gateway_health=0.99, timestamp=1760000000, subseed=1)
    assert success is True
    assert pmt.status == "AUTHORIZED"
    assert fcode is None
