# ULTRON v5.0 Truth Reconciliation Engine

## 1. Reconciliation-First Principle
If an external API call or webhook enters an uncertain state (timeouts, connection reset, 5xx):
$$\text{UNKNOWN} \longrightarrow \text{RECONCILE} \longrightarrow \text{PROVIDER TRUTH} \longrightarrow \text{CANONICAL STATE}$$

Blind retries on ambiguous states are strictly prohibited.

## 2. Double-Entry Invariant
Every reconciled financial state mutation generates balanced double-entry ledger records where $\sum \text{Debits} == \sum \text{Credits}$.
