# ULTRON v5.0 Razorpay Test Integration

## 1. Capabilities & Supported Operations
- **Payment & Order Retrieval**: `get_payment()`, `get_payment_status()`
- **Payment Link Recovery**: `create_payment_link()`, `get_payment_link()`, `cancel_payment_link()`
- **Webhook Verification**: Cryptographic HMAC-SHA256 signature verification (`X-Razorpay-Signature`)
- **Event Normalization**: Native `payment.failed`, `payment.captured`, `payment_link.paid` mapped to canonical events.

## 2. Ananya Textiles Demo Execution
- **Customer**: Ananya Textiles
- **Amount**: ₹24,700.00 (`2470000` paise)
- **Initial Failure**: ISO 91 Issuer Timeout
- **Autonomous Recovery Action**: `SEND_PAYMENT_LINK` $\rightarrow$ `https://rzp.io/i/plink_demo_24700`
- **Settlement**: Verified via `payment_link.paid` webhook and balanced on double-entry ledger.
