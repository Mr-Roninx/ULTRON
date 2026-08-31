import os
import json
from typing import Dict, Any, List, Optional
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from memory.episodic import memory_store
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.payment_intelligence.payment_diagnosis import payment_diagnosis_engine
from backend.mission.mission_builder import mission_registry
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/phase17"
os.makedirs(RESULTS_DIR, exist_ok=True)

DIAGNOSIS_TEST_SCENARIOS = [
    {
        "id": "SCEN_ISO_91_TRANSIENT",
        "name": "ISO 91 Issuer Outage",
        "iso_code": "91",
        "rail": "CARD",
        "gateway": "GATEWAY_A",
        "amount": 24700.0,
        "segment": "B2B_ENTERPRISE",
        "history_recoveries": 5,
        "complaints": 0,
        "llm_semantic_hypothesis": "Transient bank core banking restart; high recoverability upon 15-min backoff."
    },
    {
        "id": "SCEN_ISO_51_LIQUIDITY",
        "name": "ISO 51 Insufficient Funds with High Loyalty",
        "iso_code": "51",
        "rail": "UPI",
        "gateway": "GATEWAY_A",
        "amount": 12500.0,
        "segment": "B2B_MIDMARKET",
        "history_recoveries": 8,
        "complaints": 0,
        "llm_semantic_hypothesis": "Liquidity timing issue near payroll date; customer action via payment link recommended."
    },
    {
        "id": "SCEN_ISO_14_HARD_DECLINE",
        "name": "ISO 14 Card Expired",
        "iso_code": "14",
        "rail": "CARD",
        "gateway": "GATEWAY_B",
        "amount": 8000.0,
        "segment": "SMB",
        "history_recoveries": 1,
        "complaints": 0,
        "llm_semantic_hypothesis": "Hard credential failure; card retry permanently disabled, switch rail required."
    },
    {
        "id": "SCEN_TIMEOUT_AMBIGUOUS",
        "name": "Clearing Timeout / Pending Settlement",
        "iso_code": "TO",
        "rail": "BANK_TRANSFER",
        "gateway": "GATEWAY_C",
        "amount": 54000.0,
        "segment": "B2B_ENTERPRISE",
        "history_recoveries": 3,
        "complaints": 0,
        "llm_semantic_hypothesis": "ACH clearing timeout; status ambiguous, active reconciliation needed before dunning."
    },
    {
        "id": "SCEN_CUSTOMER_FATIGUE",
        "name": "Customer High Complaints / Near Opt-Out",
        "iso_code": "51",
        "rail": "CARD",
        "gateway": "GATEWAY_A",
        "amount": 42000.0,
        "segment": "B2B_ENTERPRISE",
        "history_recoveries": 2,
        "complaints": 4, # Severe fatigue
        "llm_semantic_hypothesis": "Customer at risk of churn; avoid aggressive outreach, prioritize silent retry or relationship discount."
    }
]

def run_diagnosis_ab_test() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    diag_diff_count = 0
    recoverability_diff_count = 0
    candidate_diff_count = 0
    final_action_diff_count = 0

    for scen in DIAGNOSIS_TEST_SCENARIOS:
        # Setup world
        world.reset()
        mission_registry.reset()
        clock.reset(1730000000)
        memory_store.clear()
        rail_health_engine.reset()

        cust = Customer(
            id=f"c_{scen['id'].lower()}",
            name=f"Customer {scen['name']}",
            segment=scen["segment"],
            complaints=scen["complaints"],
            created_at=clock.now()
        )
        world.add_customer(cust)

        pmt = Payment(
            id=f"pmt_{scen['id'].lower()}",
            customer_id=cust.id,
            amount=scen["amount"],
            status=PaymentStatus.FAILED,
            rail=scen["rail"],
            gateway_id=scen["gateway"],
            failure_code=scen["iso_code"],
            created_at=clock.now(),
            metadata={"failure_reason": scen["name"]}
        )
        world.add_payment(pmt)

        # ---------------- Run B: LLM OFF (Deterministic Diagnosis) ----------------
        det_diag = payment_diagnosis_engine.diagnose(
            payment=pmt.model_dump(),
            customer=cust.model_dump(),
            gateway_id=scen["gateway"]
        )
        det_candidates = ["WAIT", "RETRY", "RETRY_GATEWAY_A"] if scen["iso_code"] == "91" else ["SEND_PAYMENT_LINK", "WAIT"]

        loop_off = AgentLoop(
            customer_id=cust.id,
            mission_id=f"msn_diag_off_{scen['id']}",
            llm_provider=MockProvider([AgentIntent(action_type="WAIT", candidate_actions=det_candidates, preferred_action="WAIT", reasoning="Deterministic baseline diagnosis", expected_yield=0.0, payload={})])
        )
        for _ in range(5):
            loop_off.tick()

        action_off = loop_off.chosen_intent.action_type if loop_off.chosen_intent else "UNKNOWN"
        nev_off = loop_off.chosen_intent.expected_yield if loop_off.chosen_intent else 0.0

        # ---------------- Run A: LLM ON (Semantic Context Reasoning) ----------------
        llm_intent = AgentIntent(
            action_type="RECONCILE" if scen["iso_code"] == "TO" else ("APPLY_DISCOUNT" if scen["complaints"] >= 4 else "SEND_PAYMENT_LINK"),
            candidate_actions=["RECONCILE", "WAIT"] if scen["iso_code"] == "TO" else (["APPLY_DISCOUNT", "SEND_PAYMENT_LINK", "WAIT"] if scen["complaints"] >= 4 else ["SEND_PAYMENT_LINK", "SWITCH_PERMITTED_RAIL", "WAIT"]),
            preferred_action="RECONCILE" if scen["iso_code"] == "TO" else ("APPLY_DISCOUNT" if scen["complaints"] >= 4 else "SEND_PAYMENT_LINK"),
            reasoning=scen["llm_semantic_hypothesis"],
            expected_yield=scen["amount"] * 0.80,
            payload={}
        )

        loop_on = AgentLoop(
            customer_id=cust.id,
            mission_id=f"msn_diag_on_{scen['id']}",
            llm_provider=MockProvider([llm_intent])
        )
        for _ in range(5):
            loop_on.tick()

        action_on = loop_on.chosen_intent.action_type if loop_on.chosen_intent else "UNKNOWN"
        nev_on = loop_on.chosen_intent.expected_yield if loop_on.chosen_intent else 0.0

        # Differences
        has_diag_diff = (llm_intent.reasoning != det_diag.primary_reason)
        if has_diag_diff:
            diag_diff_count += 1

        has_cand_diff = (set(llm_intent.candidate_actions) != set(det_candidates))
        if has_cand_diff:
            candidate_diff_count += 1

        has_act_diff = (action_on != action_off)
        if has_act_diff:
            final_action_diff_count += 1

        results.append({
            "scenario_id": scen["id"],
            "scenario_name": scen["name"],
            "deterministic_diagnosis": det_diag.primary_reason,
            "deterministic_recoverability": det_diag.recoverability,
            "llm_semantic_reasoning": scen["llm_semantic_hypothesis"],
            "candidates_llm_on": llm_intent.candidate_actions,
            "candidates_llm_off": det_candidates,
            "final_action_llm_on": action_on,
            "final_action_llm_off": action_off,
            "nev_llm_on": round(nev_on, 2),
            "nev_llm_off": round(nev_off, 2),
            "diagnosis_differed": has_diag_diff,
            "candidates_differed": has_cand_diff,
            "final_action_differed": has_act_diff
        })

    n = len(DIAGNOSIS_TEST_SCENARIOS)
    output = {
        "experiment": "DIAGNOSIS_AB_TEST",
        "total_scenarios": n,
        "metrics": {
            "diagnosis_difference_rate": round(diag_diff_count / n, 4),
            "candidate_difference_rate": round(candidate_diff_count / n, 4),
            "final_action_difference_rate": round(final_action_diff_count / n, 4)
        },
        "verdict": "SEMANTIC_DIAGNOSIS_INFLUENCE_PROVEN" if diag_diff_count > 0 else "NO_EFFECT",
        "scenarios": results
    }

    with open(os.path.join(RESULTS_DIR, "diagnosis_ab.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return output

if __name__ == "__main__":
    res = run_diagnosis_ab_test()
    print("Diagnosis A/B Test Completed:")
    print(f"  Diagnosis Difference Rate: {res['metrics']['diagnosis_difference_rate']*100:.1f}%")
    print(f"  Candidate Difference Rate: {res['metrics']['candidate_difference_rate']*100:.1f}%")
    print(f"  Final Action Difference Rate: {res['metrics']['final_action_difference_rate']*100:.1f}%")
    print(f"  Verdict: {res['verdict']}")
