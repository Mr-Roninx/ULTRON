# ULTRON v5.0 Razorpay Webhook Gateway

## 1. Webhook Pipeline
```
    POST /webhooks/razorpay
               ↓
    RAW BODY HMAC-SHA256 VERIFICATION
               ↓
    EVENT ID + PAYLOAD HASH DEDUPLICATION
               ↓
    PERSIST TO EVENT STORE
               ↓
    NORMALIZE TO CANONICAL EVENT
               ↓
    DISPATCH TO ULTRON MISSION
```

## 2. Invariants
- Signatures are computed using the raw unmodified request body.
- Invalid or forged signatures return HTTP 400 with zero financial mutations.
