import pytest
from synthetic_payment_universe.world_v15.behavior.customer_fatigue import CustomerFatigueModel, LongHorizonFatigueState, FatigueThreshold

def test_fatigue_threshold_dynamics():
    state = LongHorizonFatigueState()
    assert CustomerFatigueModel.get_threshold(state.rolling_24h) == FatigueThreshold.NORMAL

    # Add repeated contact
    CustomerFatigueModel.apply_contact(state, 0.70, now=1760000000)
    assert CustomerFatigueModel.get_threshold(state.rolling_24h) == FatigueThreshold.HIGH

    CustomerFatigueModel.apply_contact(state, 0.20, now=1760000100)
    assert CustomerFatigueModel.get_threshold(state.rolling_24h) == FatigueThreshold.CRITICAL
