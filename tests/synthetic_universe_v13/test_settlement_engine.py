import pytest
from synthetic_payment_universe.world_v13.economy.payment_economy import PaymentCivilizationEntity
from synthetic_payment_universe.world_v13.economy.settlement_economy import SettlementEconomyEngine

def test_settlement_batching():
    p1 = PaymentCivilizationEntity(payment_id="p1", customer_id="c1", merchant_id="m1", amount=10000.0)
    p2 = PaymentCivilizationEntity(payment_id="p2", customer_id="c2", merchant_id="m1", amount=20000.0)

    batch = SettlementEconomyEngine.create_batch("GATEWAY_A", "m1", [p1, p2], 1760000000, fee_rate=0.015)
    assert batch.gross_amount == 30000.0
    assert batch.fee_amount == 450.0
    assert batch.net_amount == 29550.0
