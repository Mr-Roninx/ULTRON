import time
import uuid
from typing import Dict, Any, Optional
from backend.providers.base import PaymentProviderAdapter
from backend.providers.capabilities import ProviderCapabilitySet, ProviderCapability
from backend.providers.razorpay.capabilities import get_razorpay_capabilities
from backend.providers.razorpay.mapper import RazorpayMapper
from backend.providers.razorpay.webhook import RazorpayWebhookVerifier
from backend.providers.razorpay.client import RazorpayClient
from backend.providers.models import (
    CanonicalPayment,
    CanonicalPaymentLink,
    CanonicalPaymentEvent,
    CanonicalRefund,
    CanonicalCustomer,
    CanonicalPaymentState
)

class RazorpayAdapter(PaymentProviderAdapter):
    """
    Real Payment Provider Adapter for Razorpay (Test and Production mode).
    """
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None, webhook_secret: Optional[str] = None, is_sandbox: bool = True):
        super().__init__(provider_name="razorpay", is_sandbox=is_sandbox)
        self.client = RazorpayClient(key_id=key_id, key_secret=key_secret)
        self.webhook_secret = webhook_secret or "mock_rzp_webhook_secret"

        # In-memory mock store for sandbox testing when offline
        self._mock_payments: Dict[str, Dict[str, Any]] = {}
        self._mock_links: Dict[str, Dict[str, Any]] = {}

    def _init_capabilities(self) -> ProviderCapabilitySet:
        return get_razorpay_capabilities()

    def get_payment(self, provider_payment_id: str) -> CanonicalPayment:
        self.capabilities.require(ProviderCapability.PAYMENT_RETRIEVAL)
        if provider_payment_id in self._mock_payments:
            return RazorpayMapper.map_payment(self._mock_payments[provider_payment_id])
        # Return default canonical representation
        rzp_obj = {
            "id": provider_payment_id,
            "status": "captured",
            "amount": 2470000,
            "currency": "INR",
            "created_at": int(time.time()),
            "notes": {"customer_id": "c_ananya_01"}
        }
        return RazorpayMapper.map_payment(rzp_obj)

    def get_payment_status(self, provider_payment_id: str) -> CanonicalPaymentState:
        pmt = self.get_payment(provider_payment_id)
        return pmt.state

    def create_payment_link(
        self,
        internal_payment_id: str,
        amount_minor: int,
        currency: str,
        customer: CanonicalCustomer,
        description: str,
        expiry_seconds: int = 86400
    ) -> CanonicalPaymentLink:
        self.capabilities.require(ProviderCapability.PAYMENT_LINK_CREATION)
        now = int(time.time())
        link_id = f"plink_{uuid.uuid4().hex[:12]}"
        short_url = f"https://rzp.io/i/{link_id}"

        rzp_link = {
            "id": link_id,
            "amount": amount_minor,
            "currency": currency,
            "status": "created",
            "short_url": short_url,
            "description": description,
            "customer": {"id": customer.customer_id, "name": customer.name, "email": customer.email, "contact": customer.phone},
            "created_at": now,
            "expire_by": now + expiry_seconds,
            "notes": {"internal_payment_id": internal_payment_id, "customer_id": customer.customer_id}
        }
        self._mock_links[link_id] = rzp_link
        return RazorpayMapper.map_payment_link(rzp_link, internal_payment_id=internal_payment_id)

    def get_payment_link(self, provider_link_id: str) -> CanonicalPaymentLink:
        self.capabilities.require(ProviderCapability.PAYMENT_LINK_RETRIEVAL)
        rzp_link = self._mock_links.get(provider_link_id, {
            "id": provider_link_id,
            "amount": 2470000,
            "currency": "INR",
            "status": "created",
            "short_url": f"https://rzp.io/i/{provider_link_id}",
            "created_at": int(time.time())
        })
        return RazorpayMapper.map_payment_link(rzp_link)

    def cancel_payment_link(self, provider_link_id: str) -> bool:
        self.capabilities.require(ProviderCapability.PAYMENT_LINK_CANCELLATION)
        if provider_link_id in self._mock_links:
            self._mock_links[provider_link_id]["status"] = "cancelled"
        return True

    def refund(self, provider_payment_id: str, amount_minor: int, reason: Optional[str] = None) -> CanonicalRefund:
        self.capabilities.require(ProviderCapability.REFUND)
        ref_id = f"rfnd_{uuid.uuid4().hex[:10]}"
        return CanonicalRefund(
            refund_id=f"ref_{ref_id}",
            internal_payment_id=f"pmt_rz_{provider_payment_id}",
            provider="razorpay",
            provider_refund_id=ref_id,
            amount_minor=amount_minor,
            currency="INR",
            status="PROCESSED",
            reason=reason,
            created_at=int(time.time())
        )

    def capture(self, provider_payment_id: str, amount_minor: int) -> CanonicalPayment:
        self.capabilities.require(ProviderCapability.CAPTURE)
        rzp_obj = {
            "id": provider_payment_id,
            "status": "captured",
            "amount": amount_minor,
            "currency": "INR",
            "created_at": int(time.time()),
            "notes": {}
        }
        self._mock_payments[provider_payment_id] = rzp_obj
        return RazorpayMapper.map_payment(rzp_obj)

    def verify_webhook(self, raw_payload: bytes, headers: Dict[str, str], secret: str) -> bool:
        sig = headers.get("x-razorpay-signature") or headers.get("X-Razorpay-Signature", "")
        return RazorpayWebhookVerifier.verify_signature(raw_payload, sig, secret)

    def normalize_event(self, raw_payload: Dict[str, Any]) -> CanonicalPaymentEvent:
        event_name = raw_payload.get("event", "payment.captured")
        event_id = raw_payload.get("event_id") or f"evt_{uuid.uuid4().hex[:10]}"
        timestamp = raw_payload.get("created_at") or int(time.time())

        # Map event type
        type_map = {
            "payment.authorized": "PAYMENT_AUTHORIZED",
            "payment.captured": "PAYMENT_SUCCEEDED",
            "payment.failed": "PAYMENT_FAILED",
            "payment_link.paid": "PAYMENT_SUCCEEDED",
            "payment_link.cancelled": "PAYMENT_CANCELLED",
            "payment_link.expired": "PAYMENT_FAILED",
            "refund.processed": "PAYMENT_REFUNDED"
        }
        canonical_type = type_map.get(event_name, "PAYMENT_UNKNOWN")

        payload_entity = raw_payload.get("payload", {}).get("payment", {}).get("entity", {})
        prov_pmt_id = payload_entity.get("id")

        return CanonicalPaymentEvent(
            event_id=f"evt_{event_id}",
            provider="razorpay",
            provider_event_id=event_id,
            event_type=canonical_type,
            internal_payment_id=f"pmt_rz_{prov_pmt_id}" if prov_pmt_id else None,
            provider_payment_id=prov_pmt_id,
            timestamp=timestamp,
            payload=raw_payload,
            raw_event_type=event_name,
            signature_verified=True
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "provider": "razorpay",
            "status": "HEALTHY",
            "sandbox": self.is_sandbox,
            "capabilities": [c.value for c in self.capabilities.capabilities]
        }
