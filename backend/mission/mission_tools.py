from typing import Dict, Any, List, Optional
from backend.mission.mission import RevenueMission
from backend.mission.mission_state import RevenueMissionState
from backend.mission.mission_builder import mission_registry, mission_builder

class MissionTools:
    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        m = mission_registry.get_by_id(mission_id)
        return m.model_dump() if m else None

    def get_customer_mission(self, customer_id: str) -> Optional[Dict[str, Any]]:
        m = mission_registry.get_by_customer(customer_id)
        if not m:
            m = mission_builder.build_or_update_mission(customer_id)
        return m.model_dump() if m else None

    def list_active_missions(self) -> List[Dict[str, Any]]:
        missions = mission_registry.get_all()
        active = [m for m in missions if m.state not in [RevenueMissionState.RECOVERED, RevenueMissionState.CLOSED]]
        return [m.model_dump() for m in active]

    def transition_mission_state(self, mission_id: str, new_state: str, reason: str = "") -> bool:
        m = mission_registry.get_by_id(mission_id)
        if not m:
            return False
        try:
            target_state = RevenueMissionState(new_state)
            m.transition_state(target_state, reason)
            return True
        except ValueError:
            return False

mission_tools = MissionTools()
