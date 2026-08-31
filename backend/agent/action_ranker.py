from typing import List, Dict, Any, Optional
from backend.agent.schemas import ActionScore
from backend.economics.engine import economic_engine
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.payment_intelligence.failure_taxonomy import failure_taxonomy
from backend.payment_intelligence.payment_diagnosis import payment_diagnosis_engine

def rank_actions(feasible_actions: List[str], context: Dict[str, Any]) -> List[ActionScore]:
    """
    Deterministically ranks feasible actions based on Net Expected Value (NEV).
    Integrates Payment Diagnosis, Rail Health, Interference, and Relationship state.
    """
    scores: List[ActionScore] = []
    customer_id = context.get("customer_id") or context.get("customer", {}).get("id") or context.get("mission", {}).get("customer_id") or ""
    
    # 1. Total exposure from active mission or interference or context
    mission = context.get("mission", {})
    total_exposure = mission.get("total_exposure", 0.0)
    if total_exposure == 0.0:
        interference = context.get("interference", {})
        total_exposure = interference.get("total_exposure", 0.0)
    if total_exposure == 0.0:
        profile = context.get("profile", {})
        total_exposure = profile.get("ltv", 5000.0)
    if total_exposure == 0.0:
        total_exposure = 5000.0

    # 2. Payment Failure Diagnosis
    diagnosis = context.get("diagnosis")
    if not diagnosis and context.get("payment"):
        diagnosis = payment_diagnosis_engine.diagnose(
            payment=context.get("payment", {}),
            customer=context.get("customer", {}),
            gateway_id=context.get("payment", {}).get("gateway_id")
        ).model_dump()

    diag_recoverability = diagnosis.get("recoverability", 0.70) if diagnosis else 0.70
    primary_reason = diagnosis.get("primary_reason", "UNKNOWN_ERROR") if diagnosis else "UNKNOWN_ERROR"
    prohibited_actions = diagnosis.get("prohibited_actions", []) if diagnosis else []

    # 3. Gateway & Rail Health
    gw_id = context.get("payment", {}).get("gateway_id", "GATEWAY_A")
    gw_health = rail_health_engine.get_gateway_health(gw_id)
    gw_prob = gw_health.success_probability

    # 4. Interference Factor
    interference_score = context.get("interference", {}).get("interference_score", 0.0)
    base_risk = 0.05 + (interference_score * 0.25)

    for action in feasible_actions:
        # Check if prohibited by diagnosis (e.g. non-retryable failure or down gateway)
        if action in prohibited_actions:
            expected_recovery = 0.0
            risk_score = 0.95
        elif action == "WAIT":
            expected_recovery = total_exposure * 0.05
            risk_score = 0.0
        elif action == "RECONCILE":
            # High recovery if payment is UNKNOWN or RECONCILING, low otherwise
            payment_status = context.get("payment", {}).get("status", "")
            if payment_status in ["UNKNOWN", "RECONCILING"]:
                expected_recovery = total_exposure * 0.85
                risk_score = 0.02
            else:
                expected_recovery = total_exposure * 0.05
                risk_score = 0.05
        elif action in ["RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "RETRY_GATEWAY_C"]:
            # Action recovery strictly modulated by failure recoverability and gateway health
            target_gw = gw_id
            if "_" in action and action != "RETRY":
                target_gw = action.replace("RETRY_", "")
            target_health = rail_health_engine.get_gateway_health(target_gw)
            expected_recovery = total_exposure * diag_recoverability * target_health.success_probability
            risk_score = base_risk + (0.4 if target_health.success_probability < 0.5 else 0.0)
        elif action in ["SWITCH_PERMITTED_RAIL", "ALTERNATE_RAIL"]:
            best_gw = rail_health_engine.get_best_gateway("CARD")
            best_health = rail_health_engine.get_gateway_health(best_gw) if best_gw else gw_health
            expected_recovery = total_exposure * diag_recoverability * best_health.success_probability * 0.95
            risk_score = base_risk * 1.1
        elif action == "SEND_PAYMENT_LINK":
            failure_cls = diagnosis.get("failure_class", "UNKNOWN") if diagnosis else "UNKNOWN"
            if failure_cls in ["INFRASTRUCTURE", "GATEWAY"]:
                cust_need_factor = 0.40 # Payment link ineffective for gateway/issuer downtime
            elif failure_cls in ["LIQUIDITY", "CREDENTIAL", "AUTHENTICATION", "ACCOUNT"]:
                cust_need_factor = 1.30 # High efficacy when customer method requires update
            elif diagnosis and diagnosis.get("customer_action_required"):
                cust_need_factor = 1.20
            else:
                cust_need_factor = 0.60
            expected_recovery = total_exposure * 0.65 * cust_need_factor
            risk_score = base_risk * 1.2
        elif action in ["SEND_MESSAGE", "EMAIL", "SMS", "REQUEST_CUSTOMER_ACTION"]:
            expected_recovery = total_exposure * 0.40
            risk_score = base_risk * 1.1
        elif action in ["REGISTER_PTP", "PTP"]:
            has_promise = context.get("promise_to_pay") or context.get("ptp_active")
            expected_recovery = total_exposure * 0.55 if has_promise else 0.0
            risk_score = base_risk * 1.3
        elif action == "ESCALATE":
            # High recovery but penalized by human ops and relationship friction
            expected_recovery = total_exposure * 0.85
            risk_score = base_risk * 1.8
        elif action == "STOP":
            expected_recovery = 0.0
            risk_score = 0.0
        else:
            expected_recovery = total_exposure * 0.10
            risk_score = base_risk

        from memory.episodic import memory_store
        mem_eff = memory_store.get_action_effectiveness(customer_id, action) if customer_id else 1.0
        expected_recovery = expected_recovery * mem_eff

        action_context = {
            "customer_id": customer_id,
            "total_exposure": total_exposure,
            "expected_yield": expected_recovery,
            "risk_score": risk_score,
            "relationship_state": context.get("relationship_state")
        }

        eval_dict = economic_engine.evaluate_action(action, action_context)

        scores.append(ActionScore(
            action=action,
            expected_recovery=eval_dict["expected_recovery"],
            financial_cost=eval_dict["financial_cost"],
            relationship_cost=eval_dict["relationship_cost"],
            operational_cost=eval_dict["operational_cost"],
            risk_cost=eval_dict["risk_cost"],
            nev=eval_dict["net_expected_value"]
        ))

    # Sort descending by NEV
    scores.sort(key=lambda s: s.nev, reverse=True)
    return scores
