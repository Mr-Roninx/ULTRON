from backend.missions.payment_mission import RealPaymentMission, RealMissionState
from backend.providers.models import CanonicalPaymentState

class MissionLifecycleCoordinator:
    """
    Coordinates state transitions for real payment missions in accordance with provider and reconciliation feedback.
    """
    @staticmethod
    def transition_state(mission: RealPaymentMission, target_state: RealMissionState) -> RealPaymentMission:
        mission.current_state = target_state
        return mission

    @staticmethod
    def handle_payment_event(mission: RealPaymentMission, new_payment_state: CanonicalPaymentState) -> RealPaymentMission:
        mission.payment_state = new_payment_state
        if new_payment_state in (CanonicalPaymentState.SETTLED, CanonicalPaymentState.CAPTURED):
            mission.current_state = RealMissionState.RECOVERED
        elif new_payment_state == CanonicalPaymentState.FAILED:
            mission.current_state = RealMissionState.DIAGNOSING
        elif new_payment_state == CanonicalPaymentState.UNKNOWN:
            mission.current_state = RealMissionState.RECONCILING
        return mission

mission_coordinator = MissionLifecycleCoordinator()
