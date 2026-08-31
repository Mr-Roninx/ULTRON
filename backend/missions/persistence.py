from typing import Dict, Optional, List
from backend.missions.payment_mission import RealPaymentMission

class MissionPersistenceStore:
    """
    Persistent in-memory & SQLite-compatible store for RealPaymentMissions.
    """
    def __init__(self):
        self._missions: Dict[str, RealPaymentMission] = {}

    def save_mission(self, mission: RealPaymentMission) -> RealPaymentMission:
        self._missions[mission.mission_id] = mission
        return mission

    def get_mission(self, mission_id: str) -> Optional[RealPaymentMission]:
        return self._missions.get(mission_id)

    def get_mission_by_payment(self, internal_payment_id: str) -> Optional[RealPaymentMission]:
        for m in self._missions.values():
            if m.internal_payment_id == internal_payment_id:
                return m
        return None

    def list_missions(self) -> List[RealPaymentMission]:
        return list(self._missions.values())

mission_store = MissionPersistenceStore()
