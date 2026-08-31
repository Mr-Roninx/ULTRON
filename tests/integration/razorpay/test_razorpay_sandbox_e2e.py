import pytest
from backend.environments.real_provider import RealProviderEnvironment
from backend.providers.models import CanonicalPaymentState

@pytest.mark.sandbox
def test_razorpay_sandbox_e2e_full_lifecycle():
    env = RealProviderEnvironment("razorpay")
    ok, res = env.execute_action(
        action_type="SEND_PAYMENT_LINK",
        customer_id="c_ananya",
        payment_id="pmt_rz_full_e2e",
        payload={
            "customer_name": "Ananya Textiles",
            "amount_minor": 2470000,
            "currency": "INR",
            "channel": "EMAIL",
            "email": "finance@ananya.com"
        }
    )
    assert ok is True
    assert res["status"] == "EXECUTED"
    assert "https://rzp.io/i/" in res["short_url"]

    # Reconcile after simulated webhook
    state, msg = env.reconcile("pmt_rz_full_e2e")
    assert state == CanonicalPaymentState.SETTLED
