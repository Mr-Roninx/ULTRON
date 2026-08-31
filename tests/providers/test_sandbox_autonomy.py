import pytest
from backend.environments.real_provider import RealProviderEnvironment

def test_sandbox_autonomous_payment_link_generation():
    env = RealProviderEnvironment("razorpay")
    ok, res = env.execute_action(
        action_type="SEND_PAYMENT_LINK",
        customer_id="c_ananya",
        payment_id="pmt_rz_test_01",
        payload={
            "customer_name": "Ananya Textiles",
            "amount_minor": 2470000,
            "currency": "INR",
            "channel": "EMAIL",
            "email": "finance@ananyatextiles.com"
        }
    )
    assert ok is True
    assert res["status"] == "EXECUTED"
    assert "https://rzp.io/i/" in res["short_url"]
    assert res["communication"]["status"] == "DELIVERED"
