import pytest
from synthetic_payment_universe.world_v14.economy.macro_shocks import MacroShockEngine, MacroEconomicShock

def test_macro_shock_scheduling():
    eng = MacroShockEngine()
    shock = MacroEconomicShock(
        shock_id="shk_1",
        shock_type="GATEWAY_DISRUPTION",
        target_entity="GATEWAY_A",
        magnitude=0.05,
        start_timestamp=1760000000,
        end_timestamp=1760086400
    )
    eng.schedule_shock(shock)

    active = eng.get_active_shocks(1760003600)
    assert len(active) == 1
    assert active[0].shock_id == "shk_1"

    inactive = eng.get_active_shocks(1760200000)
    assert len(inactive) == 0
