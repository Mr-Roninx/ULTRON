# ULTRON v5.0 Webhook Authenticity & Signature Hardening

## 1. Webhook Source Truth
We explicitly distinguish:
- `EXTERNAL_PROVIDER_ORIGINATED`: Originating from public gateway servers over the internet.
- `TEST_FIXTURE_INJECTION`: Injected via FastAPI test client / pytest.
- `INTERNAL_SIMULATION`: Generated inside the SWU simulator.

All automated test runs operate via **`TEST_FIXTURE_INJECTION`** unless live public webhook tunnels are provisioned.

---

## 2. Hardened Invariants
1. **Signature Verification Precedes Mutation**: HMAC-SHA256 signature is verified before payload parsing or mission creation.
2. **Deduplication**: SHA-256 payload hash + Event ID ensures replay attacks result in zero state mutations.
