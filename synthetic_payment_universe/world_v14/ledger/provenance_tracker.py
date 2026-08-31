from typing import Dict, Any, Optional
from pydantic import BaseModel

class ProvenanceChain(BaseModel):
    payment_id: str
    failure_code: str
    observed_timestamp: int
    diagnosis: str
    action_type: str
    execution_timestamp: int
    settlement_timestamp: int
    recovered_amount: float
    ledger_entry_id: str

class ProvenanceTracker:
    """
    Records and explains end-to-end economic recovery provenance.
    """
    def __init__(self):
        self._chains: Dict[str, ProvenanceChain] = {}

    def record(self, chain: ProvenanceChain):
        self._chains[chain.payment_id] = chain

    def explain(self, payment_id: str) -> Optional[Dict[str, Any]]:
        c = self._chains.get(payment_id)
        return c.model_dump() if c else None

provenance_tracker = ProvenanceTracker()
