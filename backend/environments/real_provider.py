import time
from typing import Dict, Any, Optional, Tuple
from backend.environments.environment import PaymentEnvironment
from backend.providers.models import CanonicalPayment, CanonicalPaymentState, CanonicalCustomer
from backend.providers.registry import provider_registry
from backend.safety.production_gate import production_gate
from backend.reconciliation.engine import reconciliation_engine
from backend.comms.dispatcher import comms_dispatcher

class RealProviderEnvironment(PaymentEnvironment):
    """
    Adapter executing ULTRON AgentLoop against real payment providers in TEST/SANDBOX mode.
    """
    def __init__(self, provider_name: str = "razorpay"):
        super().__init__(environment_name=f"{provider_name.upper()}_TEST", is_synthetic=False)
        self.provider_name = provider_name

    def observe_payment(self, payment_id: str) -> CanonicalPayment:
        adapter = provider_registry.get_provider(self.provider_name)
        return adapter.get_payment(payment_id)

    def observe_customer(self, customer_id: str) -> Dict[str, Any]:
        return {"customer_id": customer_id, "name": "Ananya Textiles", "tier": "SMB", "currency": "INR"}

    def execute_action(
        self,
        action_type: str,
        customer_id: str,
        payment_id: str,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        # 1. Production Execution Gate Check
        ok, reason = production_gate.validate_execution(
            provider=self.provider_name,
            action_type=action_type,
            amount_minor=payload.get("amount_minor", 0),
            is_live_request=False
        )
        if not ok:
            return False, {"status": "BLOCKED_BY_GATE", "reason": reason}

        adapter = provider_registry.get_provider(self.provider_name)

        if action_type == "SEND_PAYMENT_LINK":
            cust = CanonicalCustomer(
                customer_id=customer_id,
                name=payload.get("customer_name", "Valued Customer"),
                email=payload.get("email"),
                phone=payload.get("phone", "+919876543210")
            )
            link = adapter.create_payment_link(
                internal_payment_id=payment_id,
                amount_minor=payload.get("amount_minor", 2470000),
                currency=payload.get("currency", "INR"),
                customer=cust,
                description=payload.get("description", "Payment recovery")
            )
            # Dispatch communication
            comm_res = comms_dispatcher.send_payment_link_message(
                customer_id=customer_id,
                customer_name=cust.name,
                channel=payload.get("channel", "EMAIL"),
                recipient=cust.email or cust.phone,
                amount_str=f"INR {link.amount_minor / 100:.2f}",
                payment_url=link.short_url
            )
            return True, {
                "status": "EXECUTED",
                "action_type": action_type,
                "provider": self.provider_name,
                "link_id": link.link_id,
                "short_url": link.short_url,
                "communication": comm_res
            }

        elif action_type == "REFUND_PAYMENT":
            ref = adapter.refund(
                provider_payment_id=payment_id,
                amount_minor=payload.get("amount_minor", 0),
                reason=payload.get("reason")
            )
            return True, {"status": "EXECUTED", "action_type": action_type, "refund_id": ref.refund_id}

        return True, {"status": "EXECUTED", "action_type": action_type, "provider": self.provider_name}

    def reconcile(self, payment_id: str) -> Tuple[CanonicalPaymentState, str]:
        state, rec_state, msg = reconciliation_engine.reconcile_payment(
            internal_payment_id=payment_id,
            provider=self.provider_name,
            provider_payment_id=payment_id,
            current_internal_state=CanonicalPaymentState.UNKNOWN
        )
        return state, msg

    def get_health(self) -> Dict[str, Any]:
        adapter = provider_registry.get_provider(self.provider_name)
        return adapter.health_check()
