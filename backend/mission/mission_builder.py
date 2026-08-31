import uuid
from typing import Dict, Any, Optional, List
from backend.mission.mission import RevenueMission, OpportunityItem
from backend.mission.mission_state import RevenueMissionState
from simulator.world import world
from simulator.clock import clock

class MissionRegistry:
    def __init__(self):
        self._missions: Dict[str, RevenueMission] = {} # mission_id -> RevenueMission
        self._customer_mission_map: Dict[str, str] = {} # customer_id -> mission_id

    def reset(self):
        self._missions.clear()
        self._customer_mission_map.clear()

    def register(self, mission: RevenueMission):
        self._missions[mission.mission_id] = mission
        self._customer_mission_map[mission.customer_id] = mission.mission_id

    def get_by_id(self, mission_id: str) -> Optional[RevenueMission]:
        return self._missions.get(mission_id)

    def get_by_customer(self, customer_id: str) -> Optional[RevenueMission]:
        m_id = self._customer_mission_map.get(customer_id)
        if m_id:
            return self._missions.get(m_id)
        return None

    def get_all(self) -> List[RevenueMission]:
        return list(self._missions.values())

mission_registry = MissionRegistry()

class MissionBuilder:
    def build_or_update_mission(self, customer_id: str, trigger_event: Optional[Dict[str, Any]] = None) -> RevenueMission:
        now = clock.now()
        customer = world.customers.get(customer_id)
        cust_name = customer.name if customer else f"Customer {customer_id}"

        # Check existing active mission
        existing = mission_registry.get_by_customer(customer_id)
        if existing and existing.state not in [RevenueMissionState.RECOVERED, RevenueMissionState.CLOSED]:
            mission = existing
        else:
            mission_id = f"m_{customer_id}_{str(uuid.uuid4())[:6]}"
            mission = RevenueMission(
                mission_id=mission_id,
                customer_id=customer_id,
                customer_name=cust_name,
                state=RevenueMissionState.DISCOVERED,
                created_at=now,
                updated_at=now
            )
            mission_registry.register(mission)

        # 1. Scan failed or pending payments
        for p_id, p in world.payments.items():
            if p.customer_id == customer_id and p.status in ["FAILED", "UNKNOWN", "RECONCILING"]:
                mission.add_opportunity(OpportunityItem(
                    opportunity_id=p_id,
                    opportunity_type="SUBSCRIPTION" if "sub" in p_id.lower() or "plan" in str(p.metadata).lower() else "PAYMENT",
                    amount=float(p.amount),
                    status=str(p.status.value if hasattr(p.status, "value") else p.status),
                    created_at=p.created_at,
                    details={"gateway_id": getattr(p, "gateway_id", "GATEWAY_A"), "failure_code": getattr(p, "failure_code", "")}
                ))

        # 2. Scan overdue invoices
        for inv_id, inv in world.invoices.items():
            if inv.customer_id == customer_id and inv.status in ["OVERDUE", "OPEN", "FAILED"]:
                mission.add_opportunity(OpportunityItem(
                    opportunity_id=inv_id,
                    opportunity_type="INVOICE",
                    amount=float(inv.amount),
                    status=str(inv.status.value if hasattr(inv.status, "value") else inv.status),
                    created_at=inv.created_at,
                    details={"due_date": getattr(inv, "due_date", 0)}
                ))

        # 3. Scan abandoned checkouts
        for c_id, chk in world.checkouts.items():
            if chk.customer_id == customer_id and chk.status in ["ABANDONED", "PENDING"]:
                mission.add_opportunity(OpportunityItem(
                    opportunity_id=c_id,
                    opportunity_type="CHECKOUT",
                    amount=float(chk.amount),
                    status=str(chk.status.value if hasattr(chk.status, "value") else chk.status),
                    created_at=chk.created_at,
                    details={"items": getattr(chk, "items", [])}
                ))

        # Recalculate combined exposure
        mission.recalculate_exposure()
        return mission

mission_builder = MissionBuilder()
