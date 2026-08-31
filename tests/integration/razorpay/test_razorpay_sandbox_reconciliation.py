import pytest
from backend.environments.real_provider import RealProviderEnvironment
from backend.providers.models import CanonicalPaymentState

@pytest.mark.sandbox
def test_razorpay_sandbox_reconciliation_flow():
    env = RealProviderEnvironment("razorpay")
    state, msg = env.reconcile("pmt_rz_sb_101")
    assert state == CanonicalPaymentState.SETTLED
