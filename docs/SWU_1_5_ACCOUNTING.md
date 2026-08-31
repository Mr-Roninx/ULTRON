# ULTRON-SWU-1.5 Accounting & Reconciliation

## 1. Truth Reconciliation & Zero-Imbalance Conservation
- Every claimed recovery is reconciled against payment state, settlement batches, and double-entry ledger entries.
- If actual payment status is `FAILED` while an agent claims recovery, the reconciliation engine immediately flags `EVIDENCE_CONFLICT`.
- Double-entry balance: $\sum \text{Debits} == \sum \text{Credits}$ across all 100 evaluation seeds (Error = 0.0).
