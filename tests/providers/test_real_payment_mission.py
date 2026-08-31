import pytest
from backend.missions.payment_mission import RealPaymentMission, RealMissionState
from backend.missions.lifecycle import mission_coordinator
from backend.providers.models import CanonicalPaymentState

def test_real_payment_mission_lifecycle():
    mission = RealPaymentMission(
        mission_id="msn_001",
        customer_id="c_ananya",
        merchant_id="m_01",
        internal_payment_id="pmt_001",
        provider="razorpay",
        provider_payment_id="pay_001",
        amount_minor=2470000
    )
    assert mission.current_state == RealMissionState.NEW

    # Event arrives: payment settled
    mission_coordinator.handle_payment_event(mission, CanonicalPaymentState.SETTLED)
    assert mission.current_state == RealMissionState.RECOVERED
    assert mission.payment_state == CanonicalPaymentState.SETTLED
