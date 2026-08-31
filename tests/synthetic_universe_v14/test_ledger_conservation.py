import pytest
from synthetic_payment_universe.world_v14.ledger.double_entry_ledger import PopulationDoubleEntryLedger

def test_ledger_conservation():
    ledger = PopulationDoubleEntryLedger()
    ledger.record_transaction(
        transaction_id="tx_cons_1",
        source_event_id="evt_1",
        account_debit="BANK_CASH_GATEWAY_A",
        account_credit="MERCHANT_SETTLEMENT_CLEARING",
        amount=50000.0,
        timestamp=1760000000
    )
    assert ledger.verify_ledger_balance() is True
    assert ledger.account_balances["BANK_CASH_GATEWAY_A"] == 50000.0
    assert ledger.account_balances["MERCHANT_SETTLEMENT_CLEARING"] == -50000.0
