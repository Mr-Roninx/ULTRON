from typing import Dict, Any, Optional
from backend.providers.models import (
    CanonicalPayment,
    CanonicalPaymentLink,
    CanonicalPaymentEvent,
    CanonicalPaymentState,
    CanonicalPaymentFailureClass
)

class RazorpayMapper:
    """
    Translates native Razorpay objects to provider-neutral canonical models.
    """
    STATUS_MAP = {
        "created": CanonicalPaymentState.CREATED,
        "authorized": CanonicalPaymentState.AUTHORIZED,
        "captured": CanonicalPaymentState.SETTLED, # In Razorpay auto-capture, captured = settled
        "refunded": CanonicalPaymentState.REFUNDED,
        "failed": CanonicalPaymentState.FAILED
    }

    FAILURE_MAP = {
        "BAD_REQUEST_ERROR": CanonicalPaymentFailureClass.CONFIGURATION,
        "GATEWAY_ERROR": CanonicalPaymentFailureClass.INFRASTRUCTURE,
        "GATEWAY_TIMEOUT": CanonicalPaymentFailureClass.TRANSIENT,
        "SERVER_ERROR": CanonicalPaymentFailureClass.INFRASTRUCTURE,
        "INVALID_CARD": CanonicalPaymentFailureClass.CUSTOMER_ACTION_REQUIRED,
        "INSUFFICIENT_FUNDS": CanonicalPaymentFailureClass.CUSTOMER_ACTION_REQUIRED,
        "CARD_DECLINED": CanonicalPaymentFailureClass.HARD_DECLINE,
        "PAYMENT_CANCELLED": CanonicalPaymentFailureClass.CUSTOMER_ACTION_REQUIRED
    }

    @classmethod
    def map_payment(cls, rz_payment: Dict[str, Any], internal_payment_id: Optional[str] = None) -> CanonicalPayment:
        rz_status = rz_payment.get("status", "created").lower()
        state = cls.STATUS_MAP.get(rz_status, CanonicalPaymentState.UNKNOWN)

        f_code = rz_payment.get("error_code")
        f_class = cls.FAILURE_MAP.get(f_code, CanonicalPaymentFailureClass.AMBIGUOUS) if f_code else None

        return CanonicalPayment(
            internal_payment_id=internal_payment_id or f"pmt_rz_{rz_payment.get('id', 'unknown')}",
            provider="razorpay",
            provider_payment_id=rz_payment.get("id", ""),
            order_id=rz_payment.get("order_id"),
            customer_id=rz_payment.get("customer_id") or rz_payment.get("notes", {}).get("customer_id", "cust_unknown"),
            merchant_id=rz_payment.get("notes", {}).get("merchant_id", "merch_default"),
            amount_minor=int(rz_payment.get("amount", 0)),
            currency=rz_payment.get("currency", "INR").upper(),
            state=state,
            failure_class=f_class,
            failure_code=f_code,
            failure_message=rz_payment.get("error_description"),
            method=rz_payment.get("method"),
            created_at=int(rz_payment.get("created_at", 0)),
            updated_at=int(rz_payment.get("created_at", 0)),
            settled_at=int(rz_payment.get("created_at", 0)) if state == CanonicalPaymentState.SETTLED else None,
            metadata=rz_payment.get("notes", {})
        )

    @classmethod
    def map_payment_link(cls, rz_link: Dict[str, Any], internal_payment_id: Optional[str] = None) -> CanonicalPaymentLink:
        return CanonicalPaymentLink(
            link_id=f"link_{rz_link.get('id', 'unknown')}",
            internal_payment_id=internal_payment_id or rz_link.get("notes", {}).get("internal_payment_id", f"pmt_rz_{rz_link.get('id')}"),
            provider="razorpay",
            provider_link_id=rz_link.get("id", ""),
            short_url=rz_link.get("short_url", ""),
            amount_minor=int(rz_link.get("amount", 0)),
            currency=rz_link.get("currency", "INR").upper(),
            status=rz_link.get("status", "created").upper(),
            customer_id=rz_link.get("customer", {}).get("id") or rz_link.get("notes", {}).get("customer_id", "cust_unknown"),
            created_at=int(rz_link.get("created_at", 0)),
            expires_at=int(rz_link.get("expire_by", 0)) if rz_link.get("expire_by") else None,
            metadata=rz_link.get("notes", {})
        )
