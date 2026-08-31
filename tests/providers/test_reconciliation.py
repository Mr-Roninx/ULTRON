import pytest
from backend.reconciliation.engine import reconciliation_engine
from backend.providers.models import CanonicalPaymentState
from backend.reconciliation.state_machine import ReconciliationState

def test_reconciliation_resolves_external_truth():
    ext_state, rec_state, msg = reconciliation_engine.reconcile_payment(
        internal_payment_id="pmt_rz_123",
        provider="razorpay",
        provider_payment_id="pay_123",
        current_internal_state=CanonicalPaymentState.UNKNOWN
    )
    assert ext_state == CanonicalPaymentState.SETTLED
    assert rec_state == ReconciliationState.RESOLVED
    assert "State updated" in msg
