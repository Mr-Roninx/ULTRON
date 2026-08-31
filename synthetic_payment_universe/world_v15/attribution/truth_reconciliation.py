from typing import Dict, Any, Tuple

class TruthReconciliationEngine:
    """
    Compares telemetry claims against authoritative ledger entries and actual world payment state.
    """
    @staticmethod
    def reconcile(
        claimed_recovery: float,
        actual_payment_status: str,
        ledger_entry_amount: float
    ) -> Tuple[bool, str]:
        if actual_payment_status != "SETTLED" and claimed_recovery > 0:
            return False, "EVIDENCE_CONFLICT: Claimed recovery on non-settled payment"

        if abs(claimed_recovery - ledger_entry_amount) > 1e-4:
            return False, f"EVIDENCE_CONFLICT: Claimed {claimed_recovery} does not match ledger {ledger_entry_amount}"

        return True, "RECONCILIATION_MATCH"
