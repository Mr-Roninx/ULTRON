# ULTRON v5.0 Evidence Reconciliation Master Document

## 1. Objective & Core Philosophy
The objective of this phase is to establish a single, internally consistent, independently auditable source of truth for what ULTRON v5.0 has **actually verified**.

We follow the fundamental forensic rule:
$$\text{Runtime Reality} \geq \text{Test Results} \gg \text{Documentation Claims}$$

If an external network call was not observed, we strictly label the evidence as **`FIXTURE_ONLY`** or **`MOCK`**, never `PROVIDER_SANDBOX`.

---

## 2. Evidence Classification Hierarchy
- **`SWU`**: Synthetic Payment Universe simulations (390 baseline tests).
- **`FIXTURE`**: Deterministic test vectors, recorded payloads, and adapter unit/integration suites.
- **`MOCK`**: Programmatic mock responses.
- **`PROVIDER_SANDBOX`**: Live external network traffic to provider test endpoints (requires exported API keys).
- **`PROVIDER_LIVE`**: Production money execution (Strictly OUT OF SCOPE; `production_enabled=False`).
