# ULTRON v5.0 Stripe Integration

## 1. Capabilities & Supported Operations
- **PaymentIntent Lifecycle**: Mapped from `requires_payment_method`, `requires_action`, `processing` to canonical states.
- **Stripe Checkout / Payment Links**: Generated securely with currency minor units.
- **Webhook Verification**: Signature header parsing (`t=..., v1=...`) with HMAC-SHA256.
- **Test Sandbox Support**: Fully validated under `STRIPE_TEST` environment mode.
