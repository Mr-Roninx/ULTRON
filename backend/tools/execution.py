from typing import Dict, Any, Optional
from pydantic import BaseModel
from simulator.world import world
from financial.authority import authority_engine, AuthorityLevel
from financial.policy import policy_engine
from financial.risk import risk_engine
from financial.idempotency import idempotency_engine
from backend.audit.ledger import audit_ledger
from simulator.models import PaymentStatus, RecoveryAction, Communication
from simulator.clock import clock
from simulator.event_bus import event_bus
from simulator.events import DomainEvent
from simulator.customer_state import customer_state_engine
import uuid

class ToolResult(BaseModel):
    success: bool
    action_id: str
    state_change: str | None
    message: str

class ExecutionTools:
    def _validate_pipeline(self, mission_id: str, customer_id: str, action_type: str, payload: dict, max_risk: float, authority: str) -> Optional[ToolResult]:
        # 1. State / Customer Existence Validation
        if customer_id not in world.customers:
            return ToolResult(success=False, action_id="", state_change=None, message=f"Customer '{customer_id}' not found.")

        # 2. Authority Validation
        auth_level = AuthorityLevel(authority)
        if not authority_engine.is_authorized(action_type, auth_level):
            audit_ledger.log(
                event_type="AUTHORITY_REJECTION",
                actor="POLICY_ENFORCER",
                payload={"mission_id": mission_id, "customer_id": customer_id, "action_type": action_type, "authority": authority},
                mission_id=mission_id
            )
            return ToolResult(success=False, action_id="", state_change=None, message="Authority level too low")
            
        # 3. Risk Validation
        try:
            risk_engine.validate(action_type, max_risk, payload)
        except Exception as e:
            audit_ledger.log(
                event_type="RISK_REJECTION",
                actor="RISK_ENGINE",
                payload={"mission_id": mission_id, "customer_id": customer_id, "action_type": action_type, "error": str(e)},
                mission_id=mission_id
            )
            return ToolResult(success=False, action_id="", state_change=None, message=str(e))
            
        # 4. Policy Validation
        context = customer_state_engine.get_snapshot(customer_id)
        try:
            policy_engine.validate(action_type, context, payload)
        except Exception as e:
            audit_ledger.log(
                event_type="POLICY_REJECTION",
                actor="POLICY_ENGINE",
                payload={"mission_id": mission_id, "customer_id": customer_id, "action_type": action_type, "error": str(e)},
                mission_id=mission_id
            )
            return ToolResult(success=False, action_id="", state_change=None, message=str(e))

        # 5. Idempotency Check
        cached_result = idempotency_engine.check_and_record(mission_id, action_type, payload)
        if cached_result:
            audit_ledger.log(
                event_type="IDEMPOTENT_HIT",
                actor="IDEMPOTENCY_ENGINE",
                payload={"mission_id": mission_id, "action_type": action_type, "cached": cached_result},
                mission_id=mission_id
            )
            return ToolResult(
                success=True,
                action_id=cached_result.get("action_id", ""),
                state_change=cached_result.get("state_change"),
                message=f"Duplicate execution suppressed: {cached_result.get('message', 'Already executed')}"
            )
            
        return None

    def reconcile_payment(self, mission_id: str, customer_id: str, payment_id: str, authority: str, max_risk: float = 1.0) -> ToolResult:
        payload = {"payment_id": payment_id}
        rejection = self._validate_pipeline(mission_id, customer_id, "RECONCILE", payload, max_risk, authority)
        if rejection:
            return rejection
            
        from financial.reconciliation import reconciliation
        from simulator.models import PaymentStatus
        
        # Reconciliation reaches out to gateway
        success = reconciliation.reconcile(payment_id, PaymentStatus.FAILED)
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        
        if success:
            res = ToolResult(success=True, action_id=action_id, state_change="RECONCILED", message="Payment reconciled.")
        else:
            res = ToolResult(success=False, action_id=action_id, state_change=None, message="Reconciliation failed (payment not found or not UNKNOWN).")

        if res.success:
            idempotency_engine.check_and_record(mission_id, "RECONCILE", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
            world.add_recovery_action(RecoveryAction(
                id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="RECONCILE", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
            ))
            audit_ledger.log(
                event_type="TOOL_EXECUTED",
                actor="ULTRON_AGENT",
                payload={"action_type": "RECONCILE", "action_id": action_id, "payment_id": payment_id, "result": res.model_dump()},
                mission_id=mission_id
            )
        return res

    def schedule_retry(self, mission_id: str, customer_id: str, payment_id: str, delay: int, authority: str, max_risk: float = 1.0) -> ToolResult:
        payload = {"payment_id": payment_id, "delay": delay}
        rejection = self._validate_pipeline(mission_id, customer_id, "RETRY", payload, max_risk, authority)
        if rejection:
            return rejection
            
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        def _do_retry():
            if payment_id in world.payments and world.payments[payment_id].status == PaymentStatus.FAILED:
                world.update_payment_status(payment_id, PaymentStatus.INITIATED.value)
                
        clock.schedule(clock.now() + delay, _do_retry)
        res = ToolResult(success=True, action_id=action_id, state_change="RETRY_SCHEDULED", message=f"Retry scheduled in {delay} seconds.")
        
        idempotency_engine.check_and_record(mission_id, "RETRY", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
        world.add_recovery_action(RecoveryAction(
            id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="RETRY", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
        ))
        audit_ledger.log(
            event_type="TOOL_EXECUTED",
            actor="ULTRON_AGENT",
            payload={"action_type": "RETRY", "action_id": action_id, "payment_id": payment_id, "delay": delay},
            mission_id=mission_id
        )
        return res

    def generate_payment_link(self, mission_id: str, customer_id: str, items: list[str], authority: str, max_risk: float = 1.0) -> ToolResult:
        payload = {"items": sorted(items)}
        rejection = self._validate_pipeline(mission_id, customer_id, "SEND_PAYMENT_LINK", payload, max_risk, authority)
        if rejection:
            return rejection
            
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        comm = Communication(
            id=f"comm_{str(uuid.uuid4())[:8]}",
            customer_id=customer_id,
            channel="EMAIL",
            message_type="PAYMENT_LINK",
            sent_at=clock.now()
        )
        world.add_communication(comm)
        res = ToolResult(success=True, action_id=action_id, state_change="COMMUNICATION_SENT", message="Payment link generated and sent.")
        
        idempotency_engine.check_and_record(mission_id, "SEND_PAYMENT_LINK", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
        world.add_recovery_action(RecoveryAction(
            id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="SEND_PAYMENT_LINK", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
        ))
        audit_ledger.log(
            event_type="TOOL_EXECUTED",
            actor="ULTRON_AGENT",
            payload={"action_type": "SEND_PAYMENT_LINK", "action_id": action_id, "items": items, "comm_id": comm.id},
            mission_id=mission_id
        )
        return res

    def send_customer_message(self, mission_id: str, customer_id: str, channel: str, message_type: str, authority: str, max_risk: float = 1.0) -> ToolResult:
        payload = {"channel": channel, "message_type": message_type}
        rejection = self._validate_pipeline(mission_id, customer_id, "SEND_MESSAGE", payload, max_risk, authority)
        if rejection:
            return rejection
            
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        comm = Communication(
            id=f"comm_{str(uuid.uuid4())[:8]}",
            customer_id=customer_id,
            channel=channel,
            message_type=message_type,
            sent_at=clock.now()
        )
        world.add_communication(comm)
        res = ToolResult(success=True, action_id=action_id, state_change="COMMUNICATION_SENT", message=f"Message sent via {channel}.")
        
        idempotency_engine.check_and_record(mission_id, "SEND_MESSAGE", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
        world.add_recovery_action(RecoveryAction(
            id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="SEND_MESSAGE", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
        ))
        audit_ledger.log(
            event_type="TOOL_EXECUTED",
            actor="ULTRON_AGENT",
            payload={"action_type": "SEND_MESSAGE", "action_id": action_id, "channel": channel, "message_type": message_type, "comm_id": comm.id},
            mission_id=mission_id
        )
        return res

    def register_ptp(self, mission_id: str, customer_id: str, promise_date: int, authority: str, max_risk: float = 1.0) -> ToolResult:
        payload = {"promise_date": promise_date}
        rejection = self._validate_pipeline(mission_id, customer_id, "REGISTER_PTP", payload, max_risk, authority)
        if rejection:
            return rejection
            
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        event_bus.publish(DomainEvent(
            event_id=f"E_{str(uuid.uuid4())[:8]}",
            event_type="PTP_REGISTERED",
            entity_type="CUSTOMER",
            entity_id=customer_id,
            customer_id=customer_id,
            timestamp=clock.now(),
            new_state="PTP_ACTIVE",
            payload={"promise_date": promise_date}
        ))
        res = ToolResult(success=True, action_id=action_id, state_change="PTP_REGISTERED", message="Promise to pay registered.")
        
        idempotency_engine.check_and_record(mission_id, "REGISTER_PTP", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
        world.add_recovery_action(RecoveryAction(
            id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="REGISTER_PTP", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
        ))
        audit_ledger.log(
            event_type="TOOL_EXECUTED",
            actor="ULTRON_AGENT",
            payload={"action_type": "REGISTER_PTP", "action_id": action_id, "promise_date": promise_date},
            mission_id=mission_id
        )
        return res

    def escalate_to_human(self, mission_id: str, customer_id: str, reason: str, authority: str, max_risk: float = 1.0) -> ToolResult:
        payload = {"reason": reason}
        rejection = self._validate_pipeline(mission_id, customer_id, "ESCALATE", payload, max_risk, authority)
        if rejection:
            return rejection
            
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        event_bus.publish(DomainEvent(
            event_id=f"E_{str(uuid.uuid4())[:8]}",
            event_type="MISSION_ESCALATED",
            entity_type="MISSION",
            entity_id=mission_id,
            customer_id=customer_id,
            timestamp=clock.now(),
            new_state="ESCALATED",
            payload={"reason": reason}
        ))
        res = ToolResult(success=True, action_id=action_id, state_change="ESCALATED", message="Escalated to human.")
        
        idempotency_engine.check_and_record(mission_id, "ESCALATE", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
        world.add_recovery_action(RecoveryAction(
            id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="ESCALATE", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
        ))
        audit_ledger.log(
            event_type="TOOL_EXECUTED",
            actor="ULTRON_AGENT",
            payload={"action_type": "ESCALATE", "action_id": action_id, "reason": reason},
            mission_id=mission_id
        )
        return res

    def switch_permitted_rail(self, mission_id: str, customer_id: str, target_rail: str = "CARD", target_gateway: str = "GATEWAY_B", authority: str = "AUTONOMOUS", max_risk: float = 1.0) -> ToolResult:
        payload = {"target_rail": target_rail, "target_gateway": target_gateway}
        rejection = self._validate_pipeline(mission_id, customer_id, "SWITCH_PERMITTED_RAIL", payload, max_risk, authority)
        if rejection:
            return rejection
            
        action_id = f"act_{str(uuid.uuid4())[:8]}"
        res = ToolResult(success=True, action_id=action_id, state_change="RAIL_SWITCHED", message=f"Switched rail to {target_rail} on gateway {target_gateway}.")
        
        idempotency_engine.check_and_record(mission_id, "SWITCH_PERMITTED_RAIL", payload, {"action_id": action_id, "state_change": res.state_change, "message": res.message})
        world.add_recovery_action(RecoveryAction(
            id=action_id, mission_id=mission_id, customer_id=customer_id, action_type="SWITCH_PERMITTED_RAIL", status="EXECUTED", expected_value=0.0, timestamp=clock.now()
        ))
        audit_ledger.log(
            event_type="TOOL_EXECUTED",
            actor="ULTRON_AGENT",
            payload={"action_type": "SWITCH_PERMITTED_RAIL", "action_id": action_id, "target_rail": target_rail, "target_gateway": target_gateway},
            mission_id=mission_id
        )
        return res

execution_tools = ExecutionTools()
