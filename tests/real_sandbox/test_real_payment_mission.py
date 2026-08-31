import pytest
from backend.missions.payment_mission import RealPaymentMission, RealMissionState

@pytest.mark.fixture
def test_real_payment_mission_persistence_model():
    mission = RealPaymentMission(
        mission_id="msn_real_01",
        customer_id="c_ananya",
        merchant_id="m_01",
        internal_payment_id="pmt_rz_01",
        provider="razorpay",
        provider_payment_id="pay_rz_01",
        amount_minor=2470000
    )
    mission.record_action("SEND_PAYMENT_LINK", "EXECUTED", {"link_id": "plink_123"})
    assert len(mission.action_history) == 1
    assert mission.action_history[0]["action_type"] == "SEND_PAYMENT_LINK"
