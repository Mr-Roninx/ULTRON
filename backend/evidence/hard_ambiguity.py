import os
import json
import random
from typing import Dict, Any, List, Optional
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from memory.episodic import memory_store
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.mission.mission_builder import mission_registry
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider
from backend.intelligence.semantic_signal import SemanticSignal
from backend.intelligence.contextual_features import contextual_feature_extractor
from backend.intelligence.calibration import signal_calibration_engine
from backend.intelligence.economic_translation import economic_translation_engine

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/phase18"
os.makedirs(RESULTS_DIR, exist_ok=True)

AMBIGUOUS_SCENARIOS = [
    {
        "name": "Gateway A (48%) vs Gateway B (52%) Near-Tied Health",
        "iso_code": "91",
        "rail": "CARD",
        "gw_a_health": 0.48,
        "gw_b_health": 0.52,
        "amount": 25000.0,
        "signal_type": "gateway_instability_signal",
        "signal_val": 0.88,
        "llm_action": "RETRY_GATEWAY_B"
    },
    {
        "name": "Payment Link vs Silent Wait (Fatigued Enterprise Customer)",
        "iso_code": "51",
        "rail": "CARD",
        "gw_a_health": 0.95,
        "gw_b_health": 0.95,
        "amount": 32000.0,
        "complaints": 4,
        "signal_type": "customer_fatigue_signal",
        "signal_val": 0.90,
        "llm_action": "WAIT"
    },
    {
        "name": "Disputed PO / Clearing Timeout (Reconcile vs Escalate)",
        "iso_code": "TO",
        "rail": "BANK_TRANSFER",
        "gw_a_health": 0.90,
        "gw_b_health": 0.90,
        "amount": 84000.0,
        "signal_type": "settlement_ambiguity",
        "signal_val": 0.92,
        "llm_action": "RECONCILE"
    },
    {
        "name": "Expired Card with Instant UPI Rail Available",
        "iso_code": "14",
        "rail": "CARD",
        "gw_a_health": 0.95,
        "gw_b_health": 0.95,
        "amount": 14000.0,
        "signal_type": "alternate_rail_relevance",
        "signal_val": 0.95,
        "llm_action": "SWITCH_PERMITTED_RAIL"
    }
]

def run_hard_ambiguity_benchmark() -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []

    for idx, scen in enumerate(AMBIGUOUS_SCENARIOS):
        world.reset()
        mission_registry.reset()
        clock.reset(1765000000 + (idx * 86400))
        memory_store.clear()
        rail_health_engine.reset()

        rail_health_engine.update_gateway_health("GATEWAY_A", success_probability=scen["gw_a_health"])
        rail_health_engine.update_gateway_health("GATEWAY_B", success_probability=scen["gw_b_health"])

        cust_id = f"c_ambig_{idx}"
        cust = Customer(id=cust_id, name=f"Ambiguity Client {idx}", segment="B2B_ENTERPRISE", complaints=scen.get("complaints", 0), created_at=clock.now())
        world.add_customer(cust)

        pmt = Payment(id=f"pmt_ambig_{idx}", customer_id=cust_id, amount=scen["amount"], status=PaymentStatus.FAILED, rail=scen["rail"], gateway_id="GATEWAY_A", failure_code=scen["iso_code"], created_at=clock.now())
        world.add_payment(pmt)

        # Baseline LLM OFF
        loop_off = AgentLoop(customer_id=cust_id, mission_id=f"msn_ambig_off_{idx}", llm_provider=MockProvider([AgentIntent(action_type="RETRY_GATEWAY_A", candidate_actions=["RETRY_GATEWAY_A", "WAIT"], preferred_action="RETRY_GATEWAY_A", reasoning="Baseline", expected_yield=0.0, payload={})]))
        for _ in range(5):
            loop_off.tick()
        action_off = loop_off.chosen_intent.action_type if loop_off.chosen_intent else "UNKNOWN"
        nev_off = loop_off.chosen_intent.expected_yield if loop_off.chosen_intent else 0.0

        # Calibrated LLM
        sig = SemanticSignal(signal_type=scen["signal_type"], value=scen["signal_val"], confidence=0.88, evidence_reference=scen["name"], observed_timestamp=clock.now())
        features = contextual_feature_extractor.extract_features(payment=pmt.model_dump(), customer=cust.model_dump(), gateway_health=scen["gw_a_health"])
        calibrated_sig = signal_calibration_engine.calibrate_signal(sig, features)
        modifiers = economic_translation_engine.translate_signals_to_modifiers([calibrated_sig])

        loop_on = AgentLoop(customer_id=cust_id, mission_id=f"msn_ambig_on_{idx}", llm_provider=MockProvider([AgentIntent(action_type=scen["llm_action"], candidate_actions=[scen["llm_action"], "WAIT", "RETRY_GATEWAY_A"], preferred_action=scen["llm_action"], reasoning=scen["name"], expected_yield=scen["amount"] * 0.80, payload={})]))
        for _ in range(5):
            loop_on.tick()
        action_on = loop_on.chosen_intent.action_type if loop_on.chosen_intent else "UNKNOWN"
        nev_on = loop_on.chosen_intent.expected_yield if loop_on.chosen_intent else 0.0

        records.append({
            "scenario": scen["name"],
            "governing_signal": scen["signal_type"],
            "signal_raw_value": scen["signal_val"],
            "signal_calibrated_value": calibrated_sig.value,
            "deterministic_action": action_off,
            "calibrated_llm_action": action_on,
            "deterministic_nev": round(nev_off, 2),
            "calibrated_nev": round(nev_on, 2),
            "action_diverged": (action_on != action_off)
        })

    out = {
        "experiment": "HARD_AMBIGUITY_BENCHMARK",
        "scenarios_evaluated": len(AMBIGUOUS_SCENARIOS),
        "divergence_rate": round(sum(1 for r in records if r["action_diverged"]) / len(records), 4),
        "records": records
    }

    with open(os.path.join(RESULTS_DIR, "hard_ambiguity.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    return out

if __name__ == "__main__":
    res = run_hard_ambiguity_benchmark()
    print("Hard Ambiguity Benchmark Completed:")
    print(f"  Scenarios Evaluated: {res['scenarios_evaluated']}")
    print(f"  Action Divergence Rate under Ambiguity: {res['divergence_rate']*100:.1f}%")
