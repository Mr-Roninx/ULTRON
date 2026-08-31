from typing import Dict, Any, Tuple
from backend.safety.kill_switch import kill_switch_controller
from backend.safety.rate_limiter import action_rate_limiter
from backend.safety.idempotency import idempotency_manager
from backend.safety.audit_log import immutable_audit_log
from backend.agent.action_registry import action_registry

class ActionExecutionGuard:
    """
    Central safety execution boundary.
    Validates kill switches, rate limits, idempotency, and action authorization before any action execution.
    """
    @classmethod
    def validate_and_guard(
        cls,
        customer_id: str,
        payment_id: str,
        action_type: str,
        segment: str = "B2B_ENTERPRISE",
        payload: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        payload = payload or {}

        # 1. Kill Switch Check
        if not kill_switch_controller.is_action_allowed(customer_id):
            immutable_audit_log.record_event("SAFETY_GUARD", "ACTION_BLOCKED_KILL_SWITCH", {"customer_id": customer_id, "action": action_type})
            return False, "BLOCKED_BY_KILL_SWITCH"

        # 2. Action Registry Authorization
        is_auth, reason = action_registry.validate_action(action_type, segment)
        if not is_auth:
            immutable_audit_log.record_event("SAFETY_GUARD", "ACTION_UNAUTHORIZED", {"customer_id": customer_id, "action": action_type, "reason": reason})
            return False, f"UNAUTHORIZED_ACTION: {reason}"

        # 3. Rate Limiter Check
        if not action_rate_limiter.check_and_record(customer_id, action_type):
            immutable_audit_log.record_event("SAFETY_GUARD", "ACTION_RATE_LIMITED", {"customer_id": customer_id, "action": action_type})
            return False, "RATE_LIMIT_EXCEEDED"

        # 4. Idempotency Check
        idem_key = idempotency_manager.generate_key(payment_id, action_type, timestamp_bucket=int(payload.get("timestamp", 0)) // 300)
        if not idempotency_manager.claim_execution(idem_key):
            immutable_audit_log.record_event("SAFETY_GUARD", "ACTION_DUPLICATE_BLOCKED", {"customer_id": customer_id, "action": action_type, "key": idem_key})
            return False, "DUPLICATE_ACTION_BLOCKED"

        immutable_audit_log.record_event("SAFETY_GUARD", "ACTION_APPROVED", {"customer_id": customer_id, "action": action_type, "key": idem_key})
        return True, "APPROVED"

action_execution_guard = ActionExecutionGuard()
