import pytest
from synthetic_payment_universe.world_v13.economy.subscription_economy import SubscriptionEconomyEngine

def test_subscription_renewal_scheduling():
    now = 1760000000
    next_m = SubscriptionEconomyEngine.get_next_renewal_timestamp(now, "MONTHLY")
    assert next_m == now + (30 * 86400)

    next_q = SubscriptionEconomyEngine.get_next_renewal_timestamp(now, "QUARTERLY")
    assert next_q == now + (90 * 86400)
