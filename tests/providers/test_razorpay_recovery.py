import pytest
from backend.environments.real_provider import RealProviderEnvironment
from backend.integrations.webhooks.normalizer import canonical_normalizer
from backend.integrations.webhooks.deduplicator import webhook_deduplicator
from backend.reconciliation.engine import reconciliation_engine
from backend.providers.models import CanonicalPaymentState

def test_e2e_razorpay_payment_link_recovery_flow():
    env = RealProviderEnvironment("razorpay")

    # 1. Payment link creation
    ok, res = env.execute_action(
        action_type="SEND_PAYMENT_LINK",
        customer_id="c_ananya",
        payment_id="pmt_rz_e2e_01",
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
    link_id = res["link_id"]

    # 2. Simulated payment link webhook arrival
    rzp_webhook_payload = {
        "event": "payment_link.paid",
        "event_id": f"evt_link_{link_id}",
        "payload": {
            "payment": {
                "entity": {"id": "pay_rzp_e2e_settled", "amount": 2470000}
            }
        }
    }
    canonical_evt = canonical_normalizer.normalize("razorpay", rzp_webhook_payload)
    assert canonical_evt.event_type == "PAYMENT_SUCCEEDED"

    # 3. Reconciliation verification
    ext_state, msg = env.reconcile("pmt_rz_e2e_01")
    assert ext_state == CanonicalPaymentState.SETTLED
