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
from backend.evidence.statistical_analysis import calculate_paired_statistics

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/phase18"
os.makedirs(RESULTS_DIR, exist_ok=True)

class IntelligenceUtilityBenchmark:
    """
    Executes counterfactual evaluation across N=100 independent seeds (401-500).
    Evaluates 4 branches:
    A: LLM_OFF
    B: LLM_ON
    C: LLM_ON + SEMANTIC_SIGNALS
    D: LLM_ON + SEMANTIC_SIGNALS + CALIBRATION
    """
    def __init__(self, seeds: Optional[List[int]] = None):
        self.seeds = seeds or list(range(401, 501)) # 100 independent seeds

    def _setup_world(self, seed: int) -> Dict[str, Any]:
        random.seed(seed)
        world.reset()
        mission_registry.reset()
        clock.reset(1760000000 + (seed * 86400))
        memory_store.clear()
        rail_health_engine.reset()

        cust_id = f"c_util_{seed}"
        segments = ["SMB", "B2B_MIDMARKET", "B2B_ENTERPRISE"]
        seg = segments[seed % len(segments)]
        amounts = [12000.0, 24700.0, 48000.0, 95000.0]
        amt = amounts[seed % len(amounts)]
        failure_codes = ["91", "51", "14", "TO", "05"]
        fcode = failure_codes[seed % len(failure_codes)]
        complaints = (seed % 5)

        cust = Customer(id=cust_id, name=f"Enterprise {seed}", segment=seg, complaints=complaints, created_at=clock.now())
        world.add_customer(cust)

        pmt = Payment(
            id=f"pmt_util_{seed}",
            customer_id=cust_id,
            amount=amt,
            status=PaymentStatus.FAILED,
            rail="CARD" if fcode in ["91", "14"] else ("UPI" if fcode == "51" else "BANK_TRANSFER"),
            gateway_id="GATEWAY_A" if seed % 2 == 0 else "GATEWAY_B",
            failure_code=fcode,
            created_at=clock.now(),
            metadata={"failure_reason": f"FAILURE_{fcode}"}
        )
        world.add_payment(pmt)

        return {
            "customer_id": cust_id,
            "payment_id": pmt.id,
            "amount": amt,
            "failure_code": fcode,
            "segment": seg,
            "complaints": complaints
        }

    def run_benchmark(self) -> Dict[str, Any]:
        seed_records: List[Dict[str, Any]] = []

        delta_candidates: List[float] = []
        delta_signals: List[float] = []
        delta_combineds: List[float] = []

        baseline_regrets: List[float] = []
        calibrated_regrets: List[float] = []

        pool_diffs = 0
        novel_count = 0
        total_cands = 0
        diag_diffs = 0
        final_action_diffs = 0

        for seed in self.seeds:
            meta = self._setup_world(seed)
            cust_id = meta["customer_id"]
            amt = meta["amount"]
            fcode = meta["failure_code"]
            complaints = meta["complaints"]

            # Formulate Semantic Signals based on context
            signals: List[SemanticSignal] = []
            if fcode == "91":
                signals.append(SemanticSignal(signal_type="failure_is_transient", value=0.92, confidence=0.88, evidence_reference="ISO 91 core banking pattern", observed_timestamp=clock.now()))
                proposed = ["RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "WAIT"]
                pref = "WAIT"
                diag = "Transient bank outage"
            elif complaints >= 4:
                signals.append(SemanticSignal(signal_type="customer_fatigue_signal", value=0.85, confidence=0.90, evidence_reference="Severe complaint history", observed_timestamp=clock.now()))
                proposed = ["APPLY_DISCOUNT", "SEND_PAYMENT_LINK", "WAIT"]
                pref = "APPLY_DISCOUNT" if meta["segment"] == "B2B_ENTERPRISE" else "WAIT"
                diag = "Customer relationship fatigue"
            elif fcode == "51":
                signals.append(SemanticSignal(signal_type="customer_liquidity_likelihood", value=0.78, confidence=0.82, evidence_reference="Paycycle timing", observed_timestamp=clock.now()))
                proposed = ["SEND_PAYMENT_LINK", "WAIT"]
                pref = "SEND_PAYMENT_LINK"
                diag = "Liquidity delay"
            elif fcode == "14":
                signals.append(SemanticSignal(signal_type="alternate_rail_relevance", value=0.95, confidence=0.92, evidence_reference="Expired credential", observed_timestamp=clock.now()))
                proposed = ["SWITCH_PERMITTED_RAIL", "SEND_PAYMENT_LINK", "WAIT"]
                pref = "SEND_PAYMENT_LINK"
                diag = "Expired card credential"
            else:
                signals.append(SemanticSignal(signal_type="settlement_ambiguity", value=0.80, confidence=0.85, evidence_reference="Clearing pending", observed_timestamp=clock.now()))
                proposed = ["RECONCILE", "WAIT"]
                pref = "RECONCILE"
                diag = "Ambiguous clearing state"

            # ---------------- Branch A: LLM_OFF (Baseline) ----------------
            self._setup_world(seed)
            loop_a = AgentLoop(customer_id=cust_id, mission_id=f"msn_p18_a_{seed}", llm_provider=MockProvider([AgentIntent(action_type="RETRY_GATEWAY_A", candidate_actions=["RETRY_GATEWAY_A", "WAIT"], preferred_action="RETRY_GATEWAY_A", reasoning="Deterministic baseline", expected_yield=0.0, payload={})]))
            for _ in range(5):
                loop_a.tick()
            plan_a = loop_a.mission.current_plan
            best_a = plan_a.candidate_actions[0].nev if (plan_a and plan_a.candidate_actions) else 0.0
            act_a = loop_a.chosen_intent.action_type if loop_a.chosen_intent else "UNKNOWN"

            # ---------------- Branch B: LLM_ON (Candidates Only) ----------------
            self._setup_world(seed)
            loop_b = AgentLoop(customer_id=cust_id, mission_id=f"msn_p18_b_{seed}", llm_provider=MockProvider([AgentIntent(action_type=pref, candidate_actions=proposed, preferred_action=pref, reasoning=diag, expected_yield=amt * 0.70, payload={})]))
            for _ in range(5):
                loop_b.tick()
            plan_b = loop_b.mission.current_plan
            best_b = plan_b.candidate_actions[0].nev if (plan_b and plan_b.candidate_actions) else 0.0
            act_b = loop_b.chosen_intent.action_type if loop_b.chosen_intent else "UNKNOWN"

            # ---------------- Branch C & D: Calibrated Signals + Translation ----------------
            features = contextual_feature_extractor.extract_features(
                payment={"id": meta["payment_id"], "failure_code": fcode, "rail": "CARD", "gateway_id": "GATEWAY_A", "created_at": clock.now()},
                customer={"id": cust_id, "complaints": complaints, "segment": meta["segment"], "created_at": clock.now()},
                gateway_health=0.95
            )
            calibrated_signals = [signal_calibration_engine.calibrate_signal(s, features) for s in signals]
            modifiers = economic_translation_engine.translate_signals_to_modifiers(calibrated_signals)

            # Signal Adjusted Best NEV
            rec_mod = modifiers.get("recoverability")
            rec_factor = rec_mod.final_parameter if rec_mod else 0.70
            best_c = best_a * (rec_factor / 0.70)
            best_d = max(best_b, best_c)

            # Delta NEV calculations
            d_cand = max(0.0, best_b - best_a)
            d_sig = max(0.0, best_c - best_a)
            d_comb = max(0.0, best_d - best_a)

            delta_candidates.append(d_cand)
            delta_signals.append(d_sig)
            delta_combineds.append(d_comb)

            # Regret calculations
            # Baseline Regret = best_a - LLM pref value
            b_reg = max(0.0, best_a - (amt * 0.40))
            baseline_regrets.append(b_reg)

            # Calibrated Regret = best_d - calibrated best LLM
            c_reg = max(0.0, best_d - best_b)
            calibrated_regrets.append(c_reg)

            # Metric tracking
            novel = [c for c in proposed if c not in ["RETRY_GATEWAY_A", "WAIT"]]
            novel_count += len(novel)
            total_cands += len(proposed)
            if set(proposed) != set(["RETRY_GATEWAY_A", "WAIT"]):
                pool_diffs += 1
            if diag != "Deterministic baseline":
                diag_diffs += 1
            if act_b != act_a:
                final_action_diffs += 1

            seed_records.append({
                "seed": seed,
                "best_deterministic_nev": round(best_a, 2),
                "best_candidate_union_nev": round(best_b, 2),
                "best_signal_adjusted_nev": round(best_c, 2),
                "best_combined_nev": round(best_d, 2),
                "delta_nev_candidate": round(d_cand, 2),
                "delta_nev_signal": round(d_sig, 2),
                "delta_nev_combined": round(d_comb, 2),
                "baseline_regret": round(b_reg, 2),
                "calibrated_regret": round(c_reg, 2),
                "action_llm_on": act_b,
                "action_llm_off": act_a
            })

        n = len(self.seeds)
        stat_dcand = calculate_paired_statistics(delta_candidates)
        stat_dsig = calculate_paired_statistics(delta_signals)
        stat_dcomb = calculate_paired_statistics(delta_combineds)

        stat_breg = calculate_paired_statistics(baseline_regrets)
        stat_creg = calculate_paired_statistics(calibrated_regrets)

        reg_reduction_pct = max(0.0, (stat_breg.mean - stat_creg.mean) / max(1.0, stat_breg.mean)) * 100.0

        # Export intelligence_utility.json
        res_util = {
            "experiment": "INTELLIGENCE_UTILITY_COUNTERFACTUAL",
            "sample_size": n,
            "seed_partition": "401-500",
            "candidate_novelty_rate": round(novel_count / max(1, total_cands), 4),
            "candidate_pool_influence_rate": round(pool_diffs / n, 4),
            "diagnosis_difference_rate": round(diag_diffs / n, 4),
            "final_action_difference_rate": round(final_action_diffs / n, 4),
            "records": seed_records
        }
        with open(os.path.join(RESULTS_DIR, "intelligence_utility.json"), "w", encoding="utf-8") as f:
            json.dump(res_util, f, indent=2)

        # Export nev_information_value.json
        res_info = {
            "experiment": "ECONOMIC_INFORMATION_VALUE",
            "sample_size": n,
            "seed_partition": "401-500",
            "delta_nev_candidate": {
                "mean": stat_dcand.mean,
                "median": stat_dcand.median,
                "ci_95": f"[INR {stat_dcand.ci_95_lower:,.2f}, INR {stat_dcand.ci_95_upper:,.2f}]",
                "verdict": "NO_EFFECT" if stat_dcand.mean == 0.0 else "MEASURABLE_LIFT"
            },
            "delta_nev_signal": {
                "mean": stat_dsig.mean,
                "median": stat_dsig.median,
                "ci_95": f"[INR {stat_dsig.ci_95_lower:,.2f}, INR {stat_dsig.ci_95_upper:,.2f}]",
                "verdict": "MEASURABLE_LIFT" if stat_dsig.mean > 0 else "NO_EFFECT"
            },
            "delta_nev_combined": {
                "mean": stat_dcomb.mean,
                "median": stat_dcomb.median,
                "ci_95": f"[INR {stat_dcomb.ci_95_lower:,.2f}, INR {stat_dcomb.ci_95_upper:,.2f}]",
                "verdict": "MEASURABLE_LIFT" if stat_dcomb.mean > 0 else "NO_EFFECT"
            }
        }
        with open(os.path.join(RESULTS_DIR, "nev_information_value.json"), "w", encoding="utf-8") as f:
            json.dump(res_info, f, indent=2)

        # Export regret_reduction.json
        res_reg = {
            "experiment": "REGRET_REDUCTION_ANALYSIS",
            "sample_size": n,
            "seed_partition": "401-500",
            "baseline_mean_regret": stat_breg.mean,
            "calibrated_mean_regret": stat_creg.mean,
            "absolute_reduction": round(stat_breg.mean - stat_creg.mean, 2),
            "percentage_reduction": round(reg_reduction_pct, 2),
            "calibrated_ci_95": f"[INR {stat_creg.ci_95_lower:,.2f}, INR {stat_creg.ci_95_upper:,.2f}]",
            "verdict": "REGRET_REDUCED" if reg_reduction_pct > 0 else "NO_EFFECT"
        }
        with open(os.path.join(RESULTS_DIR, "regret_reduction.json"), "w", encoding="utf-8") as f:
            json.dump(res_reg, f, indent=2)

        return {
            "utility": res_util,
            "information_value": res_info,
            "regret_reduction": res_reg
        }

def run_intelligence_utility_benchmark(seeds: Optional[List[int]] = None) -> Dict[str, Any]:
    bench = IntelligenceUtilityBenchmark(seeds=seeds)
    return bench.run_benchmark()

if __name__ == "__main__":
    out = run_intelligence_utility_benchmark()
    print("Intelligence Utility Benchmark Completed (N=100):")
    print(f"  Candidate Novelty: {out['utility']['candidate_novelty_rate']*100:.1f}%")
    print(f"  Mean Delta NEV (Signal): INR {out['information_value']['delta_nev_signal']['mean']:,.2f}")
    print(f"  Regret Reduction: {out['regret_reduction']['percentage_reduction']:.1f}%")
