import pytest
from backend.environments.real_provider import RealProviderEnvironment
from backend.providers.models import CanonicalPaymentState

@pytest.mark.sandbox
def test_razorpay_sandbox_reconciliation():
    env = RealProviderEnvironment("razorpay")
    state, msg = env.reconcile("pmt_rzp_rec_sandbox")
    assert state == CanonicalPaymentState.SETTLED
