import pytest
from backend.environments.real_provider import RealProviderEnvironment
from backend.providers.models import CanonicalPaymentState

@pytest.mark.sandbox
def test_razorpay_sandbox_end_to_end():
    env = RealProviderEnvironment("razorpay")
    ok, res = env.execute_action(
        action_type="SEND_PAYMENT_LINK",
        customer_id="c_ananya",
        payment_id="pmt_rzp_e2e_clean",
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
