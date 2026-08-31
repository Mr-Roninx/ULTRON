# ULTRON v5.0 Real Sandbox Limitations & Production Gaps

## 1. Verified Sandbox Limitations
1. **Live Production Disabled**: `production_enabled=False` by default; live money execution is completely fail-closed.
2. **Provider Key Provisioning**: Razorpay was fully verified with test sandbox keys; Stripe and Adyen require active merchant keys in `.env` to execute live sandbox traffic (currently evaluated via test fixtures).
3. **Local Ingress Requirement**: Production deployment requires persistent HTTPS webhooks (e.g. ngrok / cloud ingress) to receive asynchronous gateway callbacks.

---

## 2. Production Candidate Gap Analysis
To advance from `SANDBOX_AUTONOMOUS_READY` to `PRODUCTION_CANDIDATE`:
- Production Merchant KYC & Provisioning
- Hardware Security Module (HSM) / Cloud KMS Secret Management
- PCI-DSS Scope Demarcation & Tokenization
- Real-Time SLA Monitoring & PagerDuty Integration
- Multi-Region High-Availability Gateway Failover
