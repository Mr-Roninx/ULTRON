# ULTRON v5.0 Razorpay Sandbox Run & Verification

## 1. Execution Runner
The CLI command:
```bash
python -m backend.evidence.razorpay_sandbox_verification
```
Executes the full 8-step verification sequence:
1. Validate Configuration
2. Verify Environment Guard
3. Verify Connectivity & Health
4. Execute `SEND_PAYMENT_LINK`
5. Ingest Webhook
6. Reconcile External Truth
7. Conserve Double-Entry Ledger
8. Export Tamper-Proof Trace
