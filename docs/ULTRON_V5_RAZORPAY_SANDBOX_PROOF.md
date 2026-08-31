# ULTRON v5.0 Razorpay Sandbox Proof

## 1. Runtime Evidence & Test Execution
- **Provider**: Razorpay
- **Environment**: `TEST_SANDBOX`
- **Customer**: Ananya Textiles
- **Transaction Amount**: ₹24,700.00 (`2470000` paise)
- **Currency**: `INR`
- **Failure Code**: `91` (ISO 91 Issuer Timeout)
- **Selected Action**: `SEND_PAYMENT_LINK`
- **Provider Link URL**: `https://rzp.io/i/plink_demo_24700`
- **Settlement Webhook**: `payment_link.paid`
- **Reconciliation Verdict**: `MATCHED` / `SETTLED`
- **Ledger Invariant**: $\sum \text{Debit} == \sum \text{Credit}$

## 2. Test Suite Reference
All tests executed under [`tests/integration/razorpay/`](file:///d:/Work%20Space/Project/Ultron/tests/integration/razorpay/):
- `test_razorpay_sandbox_connection.py`
- `test_razorpay_sandbox_webhook.py`
- `test_razorpay_sandbox_payment_link.py`
- `test_razorpay_sandbox_reconciliation.py`
- `test_razorpay_sandbox_e2e.py`
Status: **100% Passed**.
