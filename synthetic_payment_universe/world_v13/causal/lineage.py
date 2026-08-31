from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class RecoveryProvenance(BaseModel):
    payment_id: str
    failure_timestamp: int
    failure_code: str
    observed_by_agent_timestamp: int
    diagnosis: str
    selected_action: str
    action_execution_timestamp: int
    recovery_timestamp: int
    recovered_amount: float
    settlement_batch_id: str
    ledger_entry_id: str
    customer_relationship_delta: float

class CausalLineageEngine:
    """
    Stores and reconstructs explicit end-to-end economic provenance chains.
    """
    def __init__(self):
        self._provenance_records: Dict[str, RecoveryProvenance] = {}

    def record_provenance(self, record: RecoveryProvenance):
        self._provenance_records[record.payment_id] = record

    def explain_recovery(self, payment_id: str) -> Optional[Dict[str, Any]]:
        rec = self._provenance_records.get(payment_id)
        if not rec:
            return None
        return rec.model_dump()

causal_lineage_engine = CausalLineageEngine()
