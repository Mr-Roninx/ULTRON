import time
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field
from backend.providers.models import CanonicalPayment, CanonicalPaymentState
from backend.reconciliation.state_machine import ReconciliationState, ReconciliationStateMachine
from backend.reconciliation.mismatch import ReconciliationMismatch
from backend.reconciliation.provider_fetch import provider_fetcher
from backend.reconciliation.policy import reconciliation_policy, ReconciliationPolicyDecision

class ReconciliationRecord(BaseModel):
    reconciliation_id: str
    internal_payment_id: str
    provider: str
    provider_payment_id: str
    previous_state: CanonicalPaymentState
    resolved_state: CanonicalPaymentState
    state: ReconciliationState
    verified_at: int
    provenance: Dict[str, Any] = Field(default_factory=dict)

class ReconciliationEngine:
    """
    Reconciles external payment provider truth with internal ledger and mission state.
    """
    def __init__(self):
        self._records: Dict[str, ReconciliationRecord] = {}
        self._mismatches: List[ReconciliationMismatch] = {}

    def reconcile_payment(
        self,
        internal_payment_id: str,
        provider: str,
        provider_payment_id: str,
        current_internal_state: CanonicalPaymentState,
        force_fetch: bool = False
    ) -> Tuple[CanonicalPaymentState, ReconciliationState, Optional[str]]:
        now = int(time.time())

        # 1. Fetch Authoritative External State
        try:
            external_pmt = provider_fetcher.fetch_provider_state(provider, provider_payment_id)
            external_state = external_pmt.state
        except Exception as e:
            rec = ReconciliationRecord(
                reconciliation_id=f"rec_{internal_payment_id}_{now}",
                internal_payment_id=internal_payment_id,
                provider=provider,
                provider_payment_id=provider_payment_id,
                previous_state=current_internal_state,
                resolved_state=CanonicalPaymentState.UNKNOWN,
                state=ReconciliationState.UNKNOWN,
                verified_at=now,
                provenance={"error": str(e)}
            )
            self._records[internal_payment_id] = rec
            return CanonicalPaymentState.UNKNOWN, ReconciliationState.UNKNOWN, f"Provider fetch failed: {str(e)}"

        # 2. Check Match vs Mismatch
        if current_internal_state == external_state:
            rec_state = ReconciliationState.MATCHED
            msg = "State matched external provider truth"
        else:
            rec_state = ReconciliationState.RESOLVED
            msg = f"State updated from {current_internal_state.value} to {external_state.value} based on provider truth"

        rec = ReconciliationRecord(
            reconciliation_id=f"rec_{internal_payment_id}_{now}",
            internal_payment_id=internal_payment_id,
            provider=provider,
            provider_payment_id=provider_payment_id,
            previous_state=current_internal_state,
            resolved_state=external_state,
            state=rec_state,
            verified_at=now,
            provenance={
                "source": "PROVIDER_API",
                "method": "DIRECT_QUERY",
                "amount_minor": external_pmt.amount_minor,
                "currency": external_pmt.currency
            }
        )
        self._records[internal_payment_id] = rec
        return external_state, rec_state, msg

    def get_reconciliation(self, internal_payment_id: str) -> Optional[ReconciliationRecord]:
        return self._records.get(internal_payment_id)

reconciliation_engine = ReconciliationEngine()
