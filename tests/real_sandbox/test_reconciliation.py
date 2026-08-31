import pytest
from backend.reconciliation.engine import reconciliation_engine
from backend.providers.models import CanonicalPaymentState

@pytest.mark.fixture
def test_reconciliation_verifies_provider_truth():
    ext_state, rec_state, msg = reconciliation_engine.reconcile_payment(
        internal_payment_id="pmt_rz_audit_01",
        provider="razorpay",
        provider_payment_id="pay_audit_01",
        current_internal_state=CanonicalPaymentState.UNKNOWN
    )
    assert ext_state == CanonicalPaymentState.SETTLED
