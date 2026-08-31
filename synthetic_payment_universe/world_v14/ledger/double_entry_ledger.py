from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class PopulationLedgerEntry(BaseModel):
    entry_id: str
    transaction_id: str
    source_event_id: str
    account_debit: str
    account_credit: str
    amount: float
    currency: str = "INR"
    timestamp: int
    provenance: Dict[str, Any] = Field(default_factory=dict)

class PopulationDoubleEntryLedger:
    """
    Authoritative double-entry ledger enforcing absolute mathematical conservation.
    """
    def __init__(self):
        self.entries: List[PopulationLedgerEntry] = []
        self.account_balances: Dict[str, float] = {}

    def record_transaction(
        self,
        transaction_id: str,
        source_event_id: str,
        account_debit: str,
        account_credit: str,
        amount: float,
        timestamp: int,
        provenance: Optional[Dict[str, Any]] = None
    ) -> PopulationLedgerEntry:
        if amount <= 0:
            raise ValueError(f"Ledger transaction amount must be positive: {amount}")

        self.account_balances[account_debit] = round(self.account_balances.get(account_debit, 0.0) + amount, 2)
        self.account_balances[account_credit] = round(self.account_balances.get(account_credit, 0.0) - amount, 2)

        entry = PopulationLedgerEntry(
            entry_id=f"entry_{transaction_id}_{len(self.entries) + 1}",
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
        total = sum(self.account_balances.values())
        return abs(round(total, 2)) == 0.0
