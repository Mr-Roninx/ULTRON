# ULTRON v4.0 — Phase 18 Operational Protocol

## 1. Objective & Scope
Phase 18 defines and verifies the **Intelligence-to-Economics Bridge** (`backend/intelligence/`), transforming normalized semantic signals from the LLM into bounded economic parameters consumed by the deterministic Net Expected Value (NEV) engine, without conceding financial authority.

---

## 2. Invariants & Guardrails
1. **The LLM is NOT a Financial Authority**:
   - Zero ability to mutate balances, transfer money, or execute SQL.
   - Prohibited from directly setting expected recovery, discounts, or NEV.
2. **Normalized Semantic Signals**:
   - Strictly bounded in $[0.0, 1.0]$ with confidence $[0.0, 1.0]$ and uncertainty $[0.0, 1.0]$.
3. **Deterministic Calibration**:
   - Maximum economic modifier capped at $\pm 25\%$.
   - Out-of-distribution (OOD) and low-confidence damping enforced.
4. **Independent Evaluation Partition**:
   - Seeds `401–500` ($N=100$), completely separate from Phase 1–17 seed partitions.
5. **No Hindsight Leakage**:
   - Economic information value ($\Delta\text{NEV}$) computed strictly before execution.
