import pytest
from backend.reconciliation.engine import reconciliation_engine
from backend.providers.models import CanonicalPaymentState

@pytest.mark.fixture
def test_razorpay_reconciliation_verifies_state():
    state, rec_state, msg = reconciliation_engine.reconcile_payment(
        internal_payment_id="pmt_rzp_rec_01",
        provider="razorpay",
        provider_payment_id="pay_rzp_rec_01",
        current_internal_state=CanonicalPaymentState.UNKNOWN
    )
    assert state == CanonicalPaymentState.SETTLED
