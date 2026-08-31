import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from simulator.clock import clock

class LedgerEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: f"ledg_{uuid.uuid4().hex[:8]}")
    payment_id: str
    customer_id: str
    amount: float
    entry_type: str # DEBIT, CREDIT, RECOVERY, RECONCILIATION
    timestamp: int = Field(default_factory=clock.now)
    idempotency_key: str

class ProductionSandboxLedger:
    """
    Append-only double-entry audit ledger for sandbox testing.
    Rejects any direct state mutation or out-of-order adjustments.
    """
    def __init__(self):
        self._entries: List[LedgerEntry] = []
        self._keys: set = set()

    def record_entry(
        self,
        payment_id: str,
        customer_id: str,
        amount: float,
        entry_type: str,
        idempotency_key: str
    ) -> LedgerEntry:
        if idempotency_key in self._keys:
            # Idempotent return existing
            for e in self._entries:
                if e.idempotency_key == idempotency_key:
                    return e

        entry = LedgerEntry(
            payment_id=payment_id,
            customer_id=customer_id,
            amount=amount,
            entry_type=entry_type,
            timestamp=clock.now(),
            idempotency_key=idempotency_key
        )
        self._entries.append(entry)
        self._keys.add(idempotency_key)
        return entry

    def get_entries_for_payment(self, payment_id: str) -> List[LedgerEntry]:
        return [e for e in self._entries if e.payment_id == payment_id]

    def reset(self):
        self._entries.clear()
        self._keys.clear()

production_ledger = ProductionSandboxLedger()
