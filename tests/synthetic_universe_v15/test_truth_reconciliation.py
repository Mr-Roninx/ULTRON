import pytest
from synthetic_payment_universe.world_v15.attribution.truth_reconciliation import TruthReconciliationEngine

def test_truth_reconciliation_conflict_detection():
    # Attempting to claim recovery on a FAILED payment
    valid, msg = TruthReconciliationEngine.reconcile(
        claimed_recovery=15000.0,
        actual_payment_status="FAILED",
        ledger_entry_amount=15000.0
    )
    assert valid is False
    assert "EVIDENCE_CONFLICT" in msg
