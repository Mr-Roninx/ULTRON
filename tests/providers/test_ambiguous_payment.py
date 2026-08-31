import pytest
from backend.reconciliation.policy import reconciliation_policy, ReconciliationPolicyDecision
from backend.providers.models import CanonicalPaymentState

def test_ambiguous_payment_reconciliation_first_rule():
    # If state is UNKNOWN, policy MUST require reconciliation first before retry
    decision = reconciliation_policy.evaluate_action_safety(CanonicalPaymentState.UNKNOWN)
    assert decision == ReconciliationPolicyDecision.RECONCILE_FIRST

    # If state is SETTLED, retry is strictly forbidden
    decision_settled = reconciliation_policy.evaluate_action_safety(CanonicalPaymentState.SETTLED)
    assert decision_settled == ReconciliationPolicyDecision.DO_NOT_RETRY
