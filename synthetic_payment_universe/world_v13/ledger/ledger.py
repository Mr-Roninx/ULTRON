from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from synthetic_payment_universe.world_v13.ledger.accounts import CHART_OF_ACCOUNTS

class CivilizationLedgerEntry(BaseModel):
    entry_id: str
    transaction_id: str
    source_event_id: str
    account_debit: str
    account_credit: str
    amount: float
    currency: str = "INR"
    timestamp: int
    reconciled: bool = True
    provenance: Dict[str, Any] = Field(default_factory=dict)

class CivilizationDoubleEntryLedger:
    """
    Authoritative double-entry ledger for ULTRON-SWU-1.3.
    Guarantees that total debits equal total credits for all monetary movements.
    """
    def __init__(self):
        self.entries: List[CivilizationLedgerEntry] = []
        self.account_balances: Dict[str, float] = {acct: 0.0 for acct in CHART_OF_ACCOUNTS}

    def record_transaction(
        self,
        transaction_id: str,
        source_event_id: str,
        account_debit: str,
        account_credit: str,
        amount: float,
        timestamp: int,
        provenance: Optional[Dict[str, Any]] = None
    ) -> CivilizationLedgerEntry:
        if amount <= 0:
            raise ValueError(f"Transaction amount must be positive: {amount}")

        # Debit increases asset/expense, credit increases liability/equity/revenue
        self.account_balances[account_debit] = round(self.account_balances.get(account_debit, 0.0) + amount, 2)
        self.account_balances[account_credit] = round(self.account_balances.get(account_credit, 0.0) - amount, 2)

        entry = CivilizationLedgerEntry(
            entry_id=f"ent_{transaction_id}_{len(self.entries) + 1}",
            transaction_id=transaction_id,
            source_event_id=source_event_id,
            account_debit=account_debit,
            account_credit=account_credit,
            amount=amount,
            timestamp=timestamp,
            provenance=provenance or {}
        )
        self.entries.append(entry)
        return entry

    def verify_ledger_balance(self) -> bool:
        total_balance = sum(self.account_balances.values())
        return abs(round(total_balance, 2)) == 0.0
