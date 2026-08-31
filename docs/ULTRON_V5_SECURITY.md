# ULTRON v5.0 Security & Adversarial Hardening

## 1. Security Invariant Matrix
- **Webhook Forgery**: Invalid or forged HMAC signatures fail closed ($400\text{ Bad Request}$).
- **Credential Leakage Prevention**: API keys and secrets are never passed to LLM prompts, frontend responses, or database telemetry.
- **SQL / Tool Injection**: LLM cannot call raw SQL, shell, or arbitrary HTTP tools.
- **Production Gate**: `production_enabled=False` by default; live money mutation fails closed.
- **Kill Switch**: Instant global revocation of all autonomous execution.
