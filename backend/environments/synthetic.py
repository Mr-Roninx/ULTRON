import time
from typing import Dict, Any, Optional, Tuple
from backend.environments.environment import PaymentEnvironment
from backend.providers.models import CanonicalPayment, CanonicalPaymentState
from simulator.world import world
from backend.benchmark.firewall import TemporalObservationFirewall

class SyntheticWorldEnvironment(PaymentEnvironment):
    """
    Adapter executing ULTRON AgentLoop inside the Synthetic Payment Universe (SWU).
    """
    def __init__(self):
        super().__init__(environment_name="SWU", is_synthetic=True)

    def observe_payment(self, payment_id: str) -> CanonicalPayment:
        pmt = world.payments.get(payment_id)
        if not pmt:
            return CanonicalPayment(
                internal_payment_id=payment_id,
                provider="SWU_SIM",
                provider_payment_id=payment_id,
                customer_id="cust_unknown",
                merchant_id="merch_01",
                amount_minor=2470000,
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
        data = pmt.model_dump()
        TemporalObservationFirewall.enforce(data)
        return CanonicalPayment(
            internal_payment_id=pmt.payment_id,
            provider="SWU_SIM",
            provider_payment_id=pmt.payment_id,
            customer_id=pmt.customer_id,
            merchant_id="merch_01",
            amount_minor=int(pmt.amount * 100),
            currency=pmt.currency or "INR",
            state=CanonicalPaymentState.FAILED if pmt.status == "FAILED" else CanonicalPaymentState.SETTLED,
            created_at=pmt.created_at,
            updated_at=pmt.created_at
        )

    def observe_customer(self, customer_id: str) -> Dict[str, Any]:
        cust = world.customers.get(customer_id)
        return cust.model_dump() if cust else {}

    def execute_action(
        self,
        action_type: str,
        customer_id: str,
        payment_id: str,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        # In synthetic world, update simulated world state
        return True, {"status": "EXECUTED_SYNTHETIC", "action_type": action_type, "timestamp": int(time.time())}

    def reconcile(self, payment_id: str) -> Tuple[CanonicalPaymentState, str]:
        pmt = world.payments.get(payment_id)
        if pmt and pmt.status == "SETTLED":
            return CanonicalPaymentState.SETTLED, "Reconciled in SWU"
        return CanonicalPaymentState.FAILED, "Reconciled in SWU"

    def get_health(self) -> Dict[str, Any]:
        return {"environment": "SWU", "status": "AVAILABLE", "is_synthetic": True}
