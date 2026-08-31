# ULTRON v5.0 Razorpay Test Mode Setup

## 1. Environment Configuration
Configuration is loaded securely from `.env`:
```bash
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

## 2. Invariants
- API keys and secrets are never committed, logged, or passed to the LLM.
- All requests default strictly to `TEST` mode.
- Live/production endpoints fail closed.
