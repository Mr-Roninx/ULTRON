import pytest
from synthetic_payment_universe.schema.entities import WebhookEvent
from backend.production_sim.webhook import webhook_service

def test_webhook_anomaly_handling():
    webhook_service.reset()

    # 1. Normal dispatch
    d1 = webhook_service.dispatch_webhook(
        event_type="PAYMENT_SETTLED",
        payload={"payment_id": "p_wh_1"},
        idempotency_key="wh_key_1"
    )
    assert d1["is_duplicate"] is False

    # 2. Delayed dispatch
    d2 = webhook_service.dispatch_webhook(
        event_type="PAYMENT_PENDING",
        payload={"payment_id": "p_wh_2"},
        idempotency_key="wh_key_2",
        delay_seconds=3600
    )
    assert d2["delivered_at"] == d2["dispatched_at"] + 3600

    # 3. Duplicate webhook
    d3 = webhook_service.dispatch_webhook(
        event_type="PAYMENT_SETTLED",
        payload={"payment_id": "p_wh_1"},
        idempotency_key="wh_key_1"
    )
    assert d3["is_duplicate"] is True
