from simulator.world import world
from simulator.event_bus import event_bus
from backend.episodes.engine import episode_engine
from simulator.customer_state import customer_state_engine
from simulator.clock import clock
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.payment_intelligence.payment_diagnosis import payment_diagnosis_engine
from backend.mission.mission_tools import mission_tools
from backend.benchmark.firewall import TemporalObservationFirewall
from typing import Dict, Any, List, Optional

class InvestigationTools:
    """
    Deterministic investigation tools for ULTRON agent loop.
    Returns bounded, structured JSON conforming strictly to VirtualClock
    and passing through TemporalObservationFirewall.
    """

    def get_customer_context(self, customer_id: str) -> Dict[str, Any]:
        snapshot = customer_state_engine.get_snapshot(customer_id)
        TemporalObservationFirewall.enforce(snapshot)
        return snapshot

    def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        if customer_id in world.customers:
            data = world.customers[customer_id].model_dump()
            TemporalObservationFirewall.enforce(data)
            return data
        return {}

    def get_payment_history(self, customer_id: str) -> List[Dict[str, Any]]:
        now = clock.now()
        history = [
            p.model_dump()
            for p in world.payments.values()
            if p.customer_id == customer_id and p.created_at <= now
        ]
        TemporalObservationFirewall.enforce(history)
        return history

    def get_failed_payments(self, customer_id: str) -> List[Dict[str, Any]]:
        now = clock.now()
        failed = [
            p.model_dump()
            for p in world.payments.values()
            if p.customer_id == customer_id and p.status in ["FAILED", "UNKNOWN", "RECONCILING"] and p.created_at <= now
        ]
        TemporalObservationFirewall.enforce(failed)
        return failed

    def get_open_invoices(self, customer_id: str) -> List[Dict[str, Any]]:
        now = clock.now()
        invoices = [
            inv.model_dump()
            for inv in world.invoices.values()
            if inv.customer_id == customer_id and inv.status in ["OVERDUE", "OPEN", "FAILED"] and getattr(inv, "created_at", 0) <= now
        ]
        TemporalObservationFirewall.enforce(invoices)
        return invoices

    def get_checkout_events(self, customer_id: str) -> List[Dict[str, Any]]:
        now = clock.now()
        checkouts = [
            chk.model_dump()
            for chk in world.checkouts.values()
            if chk.customer_id == customer_id and chk.created_at <= now
        ]
        TemporalObservationFirewall.enforce(checkouts)
        return checkouts

    def get_previous_interventions(self, customer_id: str) -> List[Dict[str, Any]]:
        now = clock.now()
        actions = [
            act.model_dump()
            for act in world.recovery_actions.values()
            if act.customer_id == customer_id and act.timestamp <= now
        ]
        comms = [
            c.model_dump()
            for c in world.communications.values()
            if c.customer_id == customer_id and c.sent_at <= now
        ]
        interventions = actions + comms
        TemporalObservationFirewall.enforce(interventions)
        return interventions

    def get_gateway_health(self, gateway_id: Optional[str] = None) -> Dict[str, Any]:
        if gateway_id:
            return rail_health_engine.get_gateway_health(gateway_id).model_dump()
        return rail_health_engine.get_all_gateway_states()

    def get_rail_health(self, rail: Optional[str] = None) -> Dict[str, Any]:
        if rail:
            return rail_health_engine.get_rail_health(rail).model_dump()
        return rail_health_engine.get_all_rail_states()

    def get_relationship_state(self, customer_id: str) -> Dict[str, Any]:
        from backend.economics.relationship import relationship_model
        rel = relationship_model.get_relationship(customer_id)
        return rel.model_dump() if rel else {"sentiment": "NEUTRAL", "churn_risk": 0.1, "contact_count": 0}

    def get_active_missions(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if customer_id:
            m = mission_tools.get_customer_mission(customer_id)
            return [m] if m else []
        return mission_tools.list_active_missions()

    def get_payment_diagnosis(self, payment_id: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        payment = world.payments.get(payment_id)
        if not payment:
            return {}
        p_dict = payment.model_dump()
        cust_id = customer_id or payment.customer_id
        customer = world.customers.get(cust_id)
        c_dict = customer.model_dump() if customer else {}
        
        hist = self.get_payment_history(cust_id)
        diag = payment_diagnosis_engine.diagnose(
            payment=p_dict,
            customer=c_dict,
            gateway_id=p_dict.get("gateway_id") or "GATEWAY_A",
            raw_failure_code=p_dict.get("failure_code") or "UNKNOWN_ERROR",
            payment_history=hist
        )
        data = diag.model_dump()
        TemporalObservationFirewall.enforce(data)
        return data

    def get_related_events(self, customer_id: str, window: int = 86400 * 30) -> List[Dict[str, Any]]:
        now = clock.now()
        cutoff = now - window
        events = []
        for e in event_bus.get_history():
            if e.customer_id == customer_id and cutoff <= e.timestamp <= now:
                events.append(e.model_dump())
        TemporalObservationFirewall.enforce(events)
        return events

    def get_previous_episodes(self, customer_id: str) -> List[Dict[str, Any]]:
        episodes = episode_engine.get_episodes(customer_id)
        data = [e.model_dump() for e in episodes]
        TemporalObservationFirewall.enforce(data)
        return data

investigation_tools = InvestigationTools()
