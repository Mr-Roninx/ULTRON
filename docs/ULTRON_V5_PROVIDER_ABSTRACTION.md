# ULTRON v5.0 Provider Abstraction Layer

## 1. Provider Adapter Interface
All payment provider adapters inherit from `PaymentProviderAdapter` and expose explicit capability sets via `ProviderCapabilitySet`:
- `get_payment(provider_payment_id)`
- `get_payment_status(provider_payment_id)`
- `create_payment_link(internal_payment_id, amount_minor, currency, customer, description)`
- `get_payment_link(provider_link_id)`
- `cancel_payment_link(provider_link_id)`
- `refund(provider_payment_id, amount_minor, reason)`
- `capture(provider_payment_id, amount_minor)`
- `verify_webhook(raw_payload, headers, secret)`
- `normalize_event(raw_payload)`
- `health_check()`

## 2. Canonical Contracts & Monetary Precision
All monetary quantities are represented strictly as **integer minor units** (`amount_minor` in paise or cents), completely eliminating floating-point imprecision.
