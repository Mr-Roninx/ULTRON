import pytest
from synthetic_payment_universe.world_v13.economy.gateway_economy import GatewayEconomyEngine

def test_gateway_economy_and_health():
    engine = GatewayEconomyEngine(subseed=123)
    assert engine.get_gateway_health("GATEWAY_A") >= 0.95
    assert engine.get_gateway_health("GATEWAY_B") >= 0.90
