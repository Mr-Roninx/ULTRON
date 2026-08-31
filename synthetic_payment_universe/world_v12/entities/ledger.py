import hashlib
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from synthetic_payment_universe.world_v12.entities.base import WorldEntity

class LedgerEntry(WorldEntity):
    entry_id: str
    transaction_id: str
    source_event_id: str
    account_debit: str   # e.g. "BANK_CASH_GATEWAY_A", "ACCOUNTS_RECEIVABLE"
    account_credit: str  # e.g. "MERCHANT_SETTLEMENT_CLEARING", "CUSTOMER_INVOICE"
    amount: float
    currency: str = "INR"
    timestamp: int = 1760000000
    reconciled: bool = True
    entry_hash: str = ""

    def compute_hash(self) -> str:
        raw = f"{self.entry_id}:{self.transaction_id}:{self.account_debit}:{self.account_credit}:{self.amount}:{self.timestamp}"
        self.entry_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return self.entry_hash

class SimulatedDoubleEntryLedger:
    """
    Authoritative double-entry ledger tracking balances across merchant settlements and gateway cash holdings.
    Guarantees mathematically that total debits equal total credits.
    """
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.account_balances: Dict[str, float] = {}

    def record_transaction(
        self,
        transaction_id: str,
        source_event_id: str,
        account_debit: str,
        account_credit: str,
        amount: float,
        timestamp: int,
        currency: str = "INR"
    ) -> LedgerEntry:
        amt = round(amount, 2)
        eid = f"led_{transaction_id}_{len(self.entries) + 1}"
        entry = LedgerEntry(
            entry_id=eid,
            transaction_id=transaction_id,
            source_event_id=source_event_id,
            account_debit=account_debit,
            account_credit=account_credit,
            amount=amt,
            currency=currency,
            timestamp=timestamp
        )
        entry.compute_hash()
        self.entries.append(entry)

        # Update balance sheet
        self.account_balances[account_debit] = round(self.account_balances.get(account_debit, 0.0) + amt, 2)
        self.account_balances[account_credit] = round(self.account_balances.get(account_credit, 0.0) - amt, 2)

        return entry

    def verify_ledger_balance(self) -> bool:
        """Verifies fundamental accounting invariant: sum of all accounts equals zero."""
        total_balance = sum(self.account_balances.values())
        return abs(total_balance) < 0.01
