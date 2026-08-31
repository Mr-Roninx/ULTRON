import pytest
from synthetic_payment_universe.world_v13.ledger.ledger import CivilizationDoubleEntryLedger
from synthetic_payment_universe.world_v13.ledger.validator import LedgerConservationValidator

def test_ledger_balance_and_validation():
    ledger = CivilizationDoubleEntryLedger()
    ledger.record_transaction(
        transaction_id="tx_1",
        source_event_id="evt_1",
        account_debit="BANK_CASH_GATEWAY_A",
        account_credit="MERCHANT_SETTLEMENT_CLEARING",
        amount=45000.0,
        timestamp=1760000000
    )
    is_valid, errors = LedgerConservationValidator.validate_ledger(ledger)
    assert is_valid is True
    assert len(errors) == 0
    assert ledger.account_balances["BANK_CASH_GATEWAY_A"] == 45000.0
    assert ledger.account_balances["MERCHANT_SETTLEMENT_CLEARING"] == -45000.0
