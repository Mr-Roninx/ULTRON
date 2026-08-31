import pytest
from synthetic_payment_universe.world_v15.attribution.accounting_reconciliation import AccountingReconciliationEngine

def test_prevent_double_counting():
    # Attempting to claim recovery greater than exposure
    valid, msg = AccountingReconciliationEngine.verify_conservation(
        gross_settled_volume=50000.0,
        direct_incremental=40000.0,
        natural_recovery=20000.0,
        outstanding_exposure=50000.0
    )
    assert valid is False
    assert "Recovery violation" in msg
