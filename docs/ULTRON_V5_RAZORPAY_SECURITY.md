# ULTRON v5.0 Razorpay Security & Adversarial Protection

## 1. Security Invariants
- **Fail-Closed Production Gate**: `production_enabled=False` by default; prevents live execution.
- **Webhook Forgery Rejection**: Signatures must match HMAC-SHA256 of raw request body.
- **Replay Protection**: Event ID + payload hash deduplication blocks duplicate attacks.
- **SQL / Tool Injection Prevention**: LLM cannot invoke raw SQL or shell commands.
- **Credential Scrubbing**: Razorpay API keys and secrets are never exported in telemetry or prompt contexts.
