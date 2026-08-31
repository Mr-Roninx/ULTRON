import pytest
from backend.production_sim.webhook import webhook_service

def test_webhook_idempotent_dispatch():
    webhook_service.reset()
    
    # First dispatch
    d1 = webhook_service.dispatch_webhook(
        event_type="PAYMENT_FAILED",
        payload={"payment_id": "p_1"},
        idempotency_key="key_123"
    )
    assert d1["is_duplicate"] is False

    # Second dispatch with identical idempotency key
    d2 = webhook_service.dispatch_webhook(
        event_type="PAYMENT_FAILED",
        payload={"payment_id": "p_1"},
        idempotency_key="key_123"
    )
    assert d2["is_duplicate"] is True
