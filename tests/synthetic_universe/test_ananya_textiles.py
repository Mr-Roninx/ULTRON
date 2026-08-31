import pytest
from synthetic_payment_universe.scenarios.golden_scenarios import get_golden_scenario

def test_ananya_textiles_golden_scenario_definition():
    scen = get_golden_scenario("04_ANANYA_TEXTILES_GATEWAY_CHAOS")
    assert scen is not None
    assert scen.initial_amount == 24700.0
    assert scen.iso_failure_code == "91"
    assert len(scen.future_events) == 1
    assert scen.future_events[0]["event_type"] == "GATEWAY_DEGRADATION"
    assert scen.future_events[0]["time_offset"] == 7200
