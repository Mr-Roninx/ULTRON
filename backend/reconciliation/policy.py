from enum import Enum
from backend.providers.models import CanonicalPaymentState

class ReconciliationPolicyDecision(str, Enum):
    PROCEED_RETRY = "PROCEED_RETRY"
    RECONCILE_FIRST = "RECONCILE_FIRST"
    DO_NOT_RETRY = "DO_NOT_RETRY"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"

class ReconciliationPolicy:
    """
    Decides safety policy when an external transaction enters an uncertain state.
    """
    @staticmethod
    def evaluate_action_safety(current_internal_state: CanonicalPaymentState, last_error_type: Optional[str] = None) -> ReconciliationPolicyDecision:
        if current_internal_state in (CanonicalPaymentState.UNKNOWN, CanonicalPaymentState.RECONCILING):
            return ReconciliationPolicyDecision.RECONCILE_FIRST

        if current_internal_state in (CanonicalPaymentState.SETTLED, CanonicalPaymentState.AUTHORIZED, CanonicalPaymentState.CAPTURED):
            return ReconciliationPolicyDecision.DO_NOT_RETRY

        if last_error_type in ("TIMEOUT", "CONNECTION_RESET", "HTTP_5XX"):
            return ReconciliationPolicyDecision.RECONCILE_FIRST

        return ReconciliationPolicyDecision.PROCEED_RETRY

reconciliation_policy = ReconciliationPolicy()
