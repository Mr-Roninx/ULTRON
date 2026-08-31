# ULTRON v5.0 Razorpay Reconciliation

## 1. Truth Reconciliation Engine
Reconciliation directly queries Razorpay authoritative payment status before settling internal accounting records:

$$\text{UNKNOWN} \longrightarrow \text{Direct Razorpay Query} \longrightarrow \text{SETTLED} \longrightarrow \text{Ledger Update}$$

## 2. Monetary Precision Invariant
- Monetary amounts are tracked exclusively in **integer paise** (`amount_minor`).
- Zero binary floating-point comparisons.
- Balanced double-entry accounting: $\sum \text{Debit} == \sum \text{Credit}$.
