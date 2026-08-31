import pytest
from synthetic_payment_universe.world_v13.economy.dispute_economy import DisputeCivilizationEntity, DisputeEconomyEngine

def test_dispute_resolution():
    disp = DisputeCivilizationEntity(dispute_id="d1", payment_id="p1", amount=15000.0, created_at=1760000000)
    DisputeEconomyEngine.resolve_dispute(disp, merchant_won=True, timestamp=1760086400)
    assert disp.status == "WON"
    assert disp.resolved_at == 1760086400
