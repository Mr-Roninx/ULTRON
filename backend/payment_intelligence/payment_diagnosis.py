from typing import Dict, Any, List, Optional
from backend.payment_intelligence.schemas import (
    PaymentFailureRaw,
    NormalizedFailure,
    PaymentDiagnosis,
    FailureClass,
    FailureSeverity,
    RailHealthStatus
)
from backend.payment_intelligence.failure_normalizer import failure_normalizer
from backend.payment_intelligence.failure_taxonomy import failure_taxonomy
from backend.payment_intelligence.recoverability import recoverability_engine
from backend.payment_intelligence.rail_health import rail_health_engine
from simulator.clock import clock

class PaymentDiagnosisEngine:
    """
    Synthesizes payment failure raw inputs, customer history, gateway health,
    and policy rules into a comprehensive, deterministic PaymentDiagnosis.
    Does NOT execute actions directly.
    """
    def diagnose(
        self,
        payment: Dict[str, Any],
        customer: Optional[Dict[str, Any]] = None,
        gateway_id: Optional[str] = None,
        raw_failure_code: Optional[str] = None,
        payment_history: Optional[List[Dict[str, Any]]] = None,
        related_events: Optional[List[Dict[str, Any]]] = None,
        previous_interventions: Optional[List[Dict[str, Any]]] = None
    ) -> PaymentDiagnosis:
        customer = customer or {}
        payment_history = payment_history or []
        related_events = related_events or []
        previous_interventions = previous_interventions or []

        p_id = payment.get("id", "unknown_payment")
        c_id = payment.get("customer_id") or customer.get("id", "unknown_customer")
        gw_id = gateway_id or payment.get("gateway_id") or "GATEWAY_A"
        raw_code = raw_failure_code or payment.get("failure_code") or payment.get("raw_error") or "UNKNOWN_ERROR"
        amount = float(payment.get("amount", 0.0))
        rail = payment.get("rail") or "CARD"

        # 1. Normalize failure
        raw_failure = PaymentFailureRaw(
            gateway_id=gw_id,
            raw_code=str(raw_code),
            amount=amount,
            rail=rail,
            timestamp=clock.now()
        )
        normalized = failure_normalizer.normalize(raw_failure)

        # 2. Evaluate Rail & Gateway Health
        gw_health = rail_health_engine.get_gateway_health(gw_id)
        rail_health = rail_health_engine.get_rail_health(rail)

        # 3. Calculate dynamic recoverability
        # Past settlement rate for this customer
        past_payments = [p for p in payment_history if p.get("customer_id") == c_id]
        if past_payments:
            settled = [p for p in past_payments if p.get("status") in ["SETTLED", "SUCCESS", "COMPLETED"]]
            cust_hist_factor = max(0.6, min(1.25, (len(settled) + 1) / (len(past_payments) + 1)))
        else:
            cust_hist_factor = 1.0

        # Attempt count
        attempt_count = payment.get("attempt_count", 1)

        rec_score = recoverability_engine.calculate_recoverability(
            normalized_failure=normalized,
            attempt_count=attempt_count,
            customer_history_factor=cust_hist_factor,
            gateway_health_factor=gw_health.success_probability
        )

        # 4. Construct Evidence
        evidence = {
            "raw_code": raw_code,
            "gateway_id": gw_id,
            "gateway_health_status": gw_health.status.value,
            "gateway_success_prob": gw_health.success_probability,
            "rail": rail,
            "rail_status": rail_health.status.value,
            "attempt_count": attempt_count,
            "customer_history_factor": cust_hist_factor,
            "customer_segment": customer.get("segment", "UNKNOWN"),
            "customer_risk_band": customer.get("risk_band", "MEDIUM")
        }

        # 5. Suggested & Prohibited Actions based on taxonomy & health
        suggested = list(normalized.typical_recovery_actions)
        prohibited = list(normalized.prohibited_actions)

        # If gateway is degraded or down, retry on the same gateway is prohibited or de-prioritized
        if gw_health.status == RailHealthStatus.DOWN:
            if "RETRY" in suggested:
                suggested.remove("RETRY")
            if "RETRY" not in prohibited:
                prohibited.append("RETRY")
            if "SWITCH_PERMITTED_RAIL" not in suggested:
                suggested.insert(0, "SWITCH_PERMITTED_RAIL")

        # Compile diagnosis
        return PaymentDiagnosis(
            payment_id=p_id,
            customer_id=c_id,
            primary_reason=normalized.failure_reason,
            failure_class=normalized.failure_class,
            severity=normalized.severity,
            recoverability=rec_score,
            customer_action_required=normalized.customer_action_required,
            retry_eligible=normalized.retry_eligible and (gw_health.status != RailHealthStatus.DOWN),
            recommended_investigation=normalized.recommended_investigation,
            evidence=evidence,
            suggested_actions=suggested,
            prohibited_actions=prohibited,
            diagnosed_at=clock.now()
        )

payment_diagnosis_engine = PaymentDiagnosisEngine()
