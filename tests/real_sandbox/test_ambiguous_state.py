import pytest
from backend.reconciliation.policy import reconciliation_policy, ReconciliationPolicyDecision
from backend.providers.models import CanonicalPaymentState

@pytest.mark.fixture
def test_ambiguous_timeout_enforces_reconciliation_first():
    dec = reconciliation_policy.evaluate_action_safety(CanonicalPaymentState.UNKNOWN, last_error_type="TIMEOUT")
    assert dec == ReconciliationPolicyDecision.RECONCILE_FIRST
