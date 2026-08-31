import pytest
from synthetic_payment_universe.world_v15.ledger.adversarial_ledger import AdversarialDoubleEntryLedger

def test_ledger_conservation():
    ledger = AdversarialDoubleEntryLedger()
    ledger.record_transaction(
        transaction_id="tx_1",
        account_debit="BANK_CASH_GATEWAY_A",
        account_credit="MERCHANT_SETTLEMENT_CLEARING",
        amount=35000.0,
        timestamp=1760000000
    )
    assert ledger.verify_ledger_balance() is True
