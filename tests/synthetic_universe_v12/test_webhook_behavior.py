import pytest
from synthetic_payment_universe.world_v12.payments.webhook_system import SimulatedWebhookSystem

def test_webhook_delay_and_duplication():
    wh_sys = SimulatedWebhookSystem(subseed=123)

    # 1. Delayed webhook
    d_del = wh_sys.dispatch("PAYMENT_SETTLED", {"payment_id": "p_1"}, "key_1", timestamp=1000, force_delay_seconds=3600)
    assert d_del.status == "DELAYED"
    assert d_del.delivered_at == 4600

    # 2. Duplicate webhook
    d_dup = wh_sys.dispatch("PAYMENT_SETTLED", {"payment_id": "p_1"}, "key_1", timestamp=1005)
    assert d_dup.status == "DUPLICATE"
