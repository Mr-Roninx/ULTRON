from typing import Tuple, List
from synthetic_payment_universe.world_v13.ledger.ledger import CivilizationDoubleEntryLedger

class LedgerConservationValidator:
    """
    Validates mathematical balance and non-creation of phantom funds.
    """
    @staticmethod
    def validate_ledger(ledger: CivilizationDoubleEntryLedger) -> Tuple[bool, List[str]]:
        errors = []
        if not ledger.verify_ledger_balance():
            diff = sum(ledger.account_balances.values())
            errors.append(f"Ledger Imbalance Detected: Sum of accounts = {diff:.2f} != 0.00")
        return len(errors) == 0, errors
