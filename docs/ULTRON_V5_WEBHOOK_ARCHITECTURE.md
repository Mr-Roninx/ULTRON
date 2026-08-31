# ULTRON v5.0 Webhook Gateway Architecture

## 1. Pipeline Processing Order
```
    Raw HTTP Request Body
             ↓
    Signature Verification (HMAC-SHA256)
             ↓
    Deduplication Check (Event ID + Payload Hash)
             ↓
    Persist to Webhook Event Store
             ↓
    Normalize to CanonicalPaymentEvent
             ↓
    Dispatch to Subscribers (Missions, Reconciliation, Ledger)
```

## 2. Invariants
- Never parse or mutate financial state before signature verification succeeds.
- Never directly execute financial actions inside the synchronous HTTP handler.
