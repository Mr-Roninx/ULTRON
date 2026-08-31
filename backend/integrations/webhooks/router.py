import os
import json
import time
from fastapi import APIRouter, Request, HTTPException, Header, Response
from typing import Optional
from backend.integrations.webhooks.verifier import webhook_verifier
from backend.integrations.webhooks.deduplicator import webhook_deduplicator
from backend.integrations.webhooks.normalizer import canonical_normalizer
from backend.integrations.webhooks.event_store import webhook_event_store
from backend.integrations.webhooks.dispatcher import webhook_dispatcher
from backend.providers.errors import WebhookVerificationError

webhook_router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@webhook_router.post("/{provider}")
async def receive_provider_webhook(provider: str, request: Request):
    raw_body = await request.body()
    headers = dict(request.headers)

    # Razorpay webhook secret retrieval from environment
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET") or "mock_rzp_webhook_secret"
    if provider.lower() != "razorpay":
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' is not supported. ULTRON v5 is Razorpay-only.")

    # 1. Signature Verification (Fail-Closed)
    try:
        webhook_verifier.verify(provider, raw_body, headers, secret)
    except WebhookVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Extract Event ID
    try:
        payload_json = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    provider_event_id = payload_json.get("event_id") or payload_json.get("id") or str(hash(raw_body))

    # 3. Deduplication Check
    if webhook_deduplicator.is_duplicate(provider, provider_event_id, raw_body):
        return {"status": "DUPLICATE_IGNORED", "event_id": provider_event_id}

    rec = webhook_deduplicator.record_received(provider, provider_event_id, raw_body, int(time.time()))

    # 4. Event Normalization
    canonical_event = canonical_normalizer.normalize(provider, payload_json)

    # 5. Persist to Event Store
    webhook_event_store.store_event(canonical_event)

    # 6. Dispatch to Subscribers
    webhook_dispatcher.dispatch(canonical_event)
    webhook_deduplicator.mark_processed(rec.event_id, int(time.time()))

    return {
        "status": "PROCESSED",
        "event_id": canonical_event.event_id,
        "event_type": canonical_event.event_type,
        "provider": provider
    }
