import pytest
from synthetic_payment_universe.world_v12.entities.ledger import SimulatedDoubleEntryLedger

def test_double_entry_ledger_balance_invariant():
    ledger = SimulatedDoubleEntryLedger()

    # 1. Record 10 balanced transactions
    for i in range(10):
        ledger.record_transaction(
            transaction_id=f"tx_{i}",
            source_event_id=f"evt_{i}",
            account_debit="BANK_CASH_GATEWAY_A",
            account_credit="MERCHANT_SETTLEMENT_CLEARING",
            amount=15000.0,
            timestamp=1760000000 + (i * 100)
        )

    assert len(ledger.entries) == 10
    assert ledger.verify_ledger_balance() is True
    assert ledger.account_balances["BANK_CASH_GATEWAY_A"] == 150000.0
    assert ledger.account_balances["MERCHANT_SETTLEMENT_CLEARING"] == -150000.0
