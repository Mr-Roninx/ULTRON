from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PolicyViolationError(Exception):
    pass

class PolicyContext(BaseModel):
    customer: Dict[str, Any]
    payments: List[Dict[str, Any]] = Field(default_factory=list)
    failed_payments: List[Dict[str, Any]] = Field(default_factory=list)
    invoices: List[Dict[str, Any]] = Field(default_factory=list)
    overdue_invoices: List[Dict[str, Any]] = Field(default_factory=list)
    checkouts: List[Dict[str, Any]] = Field(default_factory=list)
    abandoned_checkouts: List[Dict[str, Any]] = Field(default_factory=list)
    total_exposure: float = 0.0
    relationship_state: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyContext":
        if not isinstance(data, dict):
            raise PolicyViolationError("Policy context must be a dictionary.")
        # Handle nested snapshot if present for backwards compatibility, but prefer flat schema
        raw = data.get("snapshot", data) if isinstance(data.get("snapshot"), dict) else data
        if "customer" not in raw or not isinstance(raw["customer"], dict):
            raise PolicyViolationError("Missing or invalid 'customer' in policy context.")
        return cls(
            customer=raw.get("customer", {}),
            payments=raw.get("payments", []),
            failed_payments=raw.get("failed_payments", []),
            invoices=raw.get("invoices", []),
            overdue_invoices=raw.get("overdue_invoices", []),
            checkouts=raw.get("checkouts", []),
            abandoned_checkouts=raw.get("abandoned_checkouts", []),
            total_exposure=raw.get("total_exposure", 0.0),
            relationship_state=raw.get("relationship_state")
        )

class PolicyEngine:
    def validate(self, action_type: str, context: Dict[str, Any] | PolicyContext, payload: Dict[str, Any]) -> bool:
        if isinstance(context, PolicyContext):
            ctx = context
        elif isinstance(context, dict):
            try:
                ctx = PolicyContext.from_dict(context)
            except PolicyViolationError:
                raise
            except Exception as e:
                raise PolicyViolationError(f"Malformed policy context: {str(e)}")
        else:
            raise PolicyViolationError(f"Unsupported context type: {type(context)}")

        customer = ctx.customer
        
        # 1. Discount Policy
        if action_type == "APPLY_DISCOUNT":
            segment = customer.get("segment")
            if segment != "B2B_ENTERPRISE":
                raise PolicyViolationError(f"Discounts only allowed for B2B_ENTERPRISE segment (current: {segment}).")
            discount_amount = payload.get("amount", 0.0)
            if discount_amount <= 0:
                raise PolicyViolationError(f"Discount amount must be strictly positive (provided: {discount_amount}).")
                
        # 2. Communication Policy during active payment processing & Amount Boundaries
        if action_type in ["SEND_MESSAGE", "SEND_PAYMENT_LINK", "REQUEST_CUSTOMER_ACTION"]:
            payments = ctx.payments
            processing = [p for p in payments if p.get("status") in ["AUTHORIZING", "AUTHORIZED"]]
            if processing:
                raise PolicyViolationError("Cannot communicate with customer while a payment is actively processing.")
                
            if action_type == "SEND_PAYMENT_LINK":
                link_amt = payload.get("amount")
                if link_amt is not None:
                    max_allowed = max(ctx.total_exposure * 2.0, 1000000.0) if ctx.total_exposure > 0 else 500000.0
                    if float(link_amt) <= 0 or float(link_amt) > max_allowed:
                        raise PolicyViolationError(f"Payment link amount {link_amt} exceeds maximum authorized exposure boundary ({max_allowed}).")

        # 3. Retry Policy & Failure Intelligence
        if action_type in ["RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "RETRY_GATEWAY_C"]:
            from financial.failure_intelligence import retryability_resolver, failure_classifier, FailureCategory
            code = payload.get("failure_code") or (ctx.failed_payments[0].get("failure_code") if ctx.failed_payments else "91")
            cat = failure_classifier.classify(str(code))
            if not retryability_resolver.is_retryable(cat):
                raise PolicyViolationError(f"Failure code {code} classified as {cat.value} which is not retryable.")

        return True

policy_engine = PolicyEngine()
