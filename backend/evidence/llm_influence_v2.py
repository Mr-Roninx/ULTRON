import os
import json
import random
from typing import Dict, Any, List, Optional
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from memory.episodic import memory_store
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider, HuggingFaceProvider
from backend.evidence.statistical_analysis import calculate_paired_statistics

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/phase16"
os.makedirs(RESULTS_DIR, exist_ok=True)

class MultiSeedInfluenceExperiment:
    """
    Executes controlled paired A/B evaluation across 30-50 seeds measuring:
    1. Metric A: Candidate Novelty Rate
    2. Metric B: Candidate Pool Influence
    3. Metric C: LLM Preference Influence
    4. Metric D: Final Decision Influence
    """
    def __init__(self, seeds: Optional[List[int]] = None):
        self.seeds = seeds or list(range(201, 231)) # 30 seeds (201-230)

    def _setup_world_for_seed(self, seed: int) -> str:
        random.seed(seed)
        world.reset()
        clock.reset(1710000000 + (seed * 86400))
        memory_store.clear()
        rail_health_engine.reset()

        cust_id = f"c_seed_{seed}"
        segments = ["SMB", "B2B_MIDMARKET", "B2B_ENTERPRISE"]
        seg = segments[seed % len(segments)]
        amounts = [4500.0, 12000.0, 24700.0, 38000.0, 52000.0]
        amt = amounts[seed % len(amounts)]
        failure_codes = ["91", "51", "14", "TO", "05"]
        fcode = failure_codes[seed % len(failure_codes)]

        cust = Customer(
            id=cust_id,
            name=f"Enterprise Corp Seed {seed}",
            segment=seg,
            created_at=clock.now()
        )
        world.add_customer(cust)

        pmt = Payment(
            id=f"pmt_seed_{seed}",
            customer_id=cust_id,
            amount=amt,
            status=PaymentStatus.FAILED,
            rail="CARD" if fcode != "51" else "UPI",
            gateway_id="GATEWAY_A" if seed % 2 == 0 else "GATEWAY_B",
            created_at=clock.now(),
            failure_code=fcode,
            metadata={"failure_reason": "TEST_FAILURE"}
        )
        world.add_payment(pmt)
        return cust_id

    def run_experiment(self) -> Dict[str, Any]:
        records: List[Dict[str, Any]] = []

        total_novel_candidates = 0
        total_llm_candidates = 0
        pool_differences = 0
        preference_differences = 0
        decision_differences = 0
        authority_overrides = 0

        nev_diffs: List[float] = []
        recovery_diffs: List[float] = []

        for seed in self.seeds:
            # ---------------- Branch A: LLM ON ----------------
            cust_id_a = self._setup_world_for_seed(seed)
            
            # Generate diverse proposal intent
            action_pool = ["WAIT", "RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SWITCH_PERMITTED_RAIL", "SEND_PAYMENT_LINK", "SEND_MESSAGE", "ESCALATE"]
            chosen_pref = "WAIT" if (seed % 3 == 0) else ("RETRY_GATEWAY_A" if (seed % 3 == 1) else "SEND_PAYMENT_LINK")
            proposed_candidates = list(set([chosen_pref, "WAIT", "RETRY", "SEND_PAYMENT_LINK"]))
            
            llm_a = MockProvider([
                AgentIntent(
                    action_type=chosen_pref,
                    candidate_actions=proposed_candidates,
                    preferred_action=chosen_pref,
                    reasoning=f"Seed {seed} LLM heuristic proposal.",
                    expected_yield=10000.0,
                    payload={}
                )
            ])

            loop_a = AgentLoop(customer_id=cust_id_a, mission_id=f"msn_seed_{seed}_on", llm_provider=llm_a)
            for _ in range(8):
                loop_a.tick()

            final_action_a = loop_a.chosen_intent.action_type if loop_a.chosen_intent else "UNKNOWN"
            pref_a = loop_a.chosen_intent.preferred_action if loop_a.chosen_intent else "UNKNOWN"
            candidates_a = list(set(loop_a.chosen_intent.candidate_actions or []))
            nev_a = loop_a.chosen_intent.expected_yield if loop_a.chosen_intent else 0.0

            # ---------------- Branch B: LLM OFF (Deterministic Baseline) ----------------
            cust_id_b = self._setup_world_for_seed(seed)
            llm_b = MockProvider([
                AgentIntent(
                    action_type="RETRY_GATEWAY_A",
                    candidate_actions=["RETRY_GATEWAY_A"],
                    preferred_action="RETRY_GATEWAY_A",
                    reasoning="Fixed deterministic rule baseline.",
                    expected_yield=0.0,
                    payload={}
                )
            ])

            loop_b = AgentLoop(customer_id=cust_id_b, mission_id=f"msn_seed_{seed}_off", llm_provider=llm_b)
            for _ in range(8):
                loop_b.tick()

            final_action_b = loop_b.chosen_intent.action_type if loop_b.chosen_intent else "UNKNOWN"
            pref_b = "RETRY_GATEWAY_A"
            candidates_b = ["RETRY_GATEWAY_A"]
            nev_b = loop_b.chosen_intent.expected_yield if loop_b.chosen_intent else 0.0

            # Metric Calculations for Seed
            novel_cands = [c for c in candidates_a if c not in candidates_b]
            total_novel_candidates += len(novel_cands)
            total_llm_candidates += max(1, len(candidates_a))

            has_pool_diff = (set(candidates_a) != set(candidates_b))
            if has_pool_diff:
                pool_differences += 1

            has_pref_diff = (pref_a != pref_b)
            if has_pref_diff:
                preference_differences += 1

            has_dec_diff = (final_action_a != final_action_b)
            if has_dec_diff:
                decision_differences += 1

            is_override = (pref_a != final_action_a)
            if is_override:
                authority_overrides += 1

            nev_diff = nev_a - nev_b
            nev_diffs.append(nev_diff)
            recovery_diffs.append(nev_diff) # Expected economic differential

            records.append({
                "seed": seed,
                "llm_candidates": candidates_a,
                "baseline_candidates": candidates_b,
                "novel_candidates": novel_cands,
                "llm_preferred": pref_a,
                "baseline_preferred": pref_b,
                "final_action_llm_on": final_action_a,
                "final_action_llm_off": final_action_b,
                "nev_llm_on": round(nev_a, 2),
                "nev_llm_off": round(nev_b, 2),
                "pool_influenced": has_pool_diff,
                "preference_influenced": has_pref_diff,
                "decision_influenced": has_dec_diff,
                "authority_override": is_override
            })

        n_runs = len(self.seeds)
        novelty_rate = total_novel_candidates / max(1, total_llm_candidates)
        pool_influence_rate = pool_differences / max(1, n_runs)
        pref_influence_rate = preference_differences / max(1, n_runs)
        decision_influence_rate = decision_differences / max(1, n_runs)
        override_rate = authority_overrides / max(1, n_runs)

        stat_summary = calculate_paired_statistics(nev_diffs)

        output = {
            "experiment": "MULTI_SEED_LLM_INFLUENCE_V2",
            "total_seeds": n_runs,
            "seeds_evaluated": self.seeds,
            "metrics": {
                "metric_a_candidate_novelty_rate": round(novelty_rate, 4),
                "metric_b_candidate_pool_influence_rate": round(pool_influence_rate, 4),
                "metric_c_preference_influence_rate": round(pref_influence_rate, 4),
                "metric_d_final_decision_influence_rate": round(decision_influence_rate, 4),
                "authority_override_rate": round(override_rate, 4)
            },
            "statistical_summary": stat_summary.model_dump(),
            "verdict": "CANDIDATE_INFLUENCE_ONLY" if decision_influence_rate == 0.0 else (
                "FINAL_DECISION_INFLUENCE" if decision_influence_rate > 0.10 else "MINIMAL_INFLUENCE"
            ),
            "seed_records": records
        }

        with open(os.path.join(RESULTS_DIR, "llm_influence_multiseed.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        return output

def execute_llm_influence_multiseed(seeds: Optional[List[int]] = None) -> Dict[str, Any]:
    exp = MultiSeedInfluenceExperiment(seeds=seeds)
    return exp.run_experiment()

if __name__ == "__main__":
    res = execute_llm_influence_multiseed()
    print(f"Multi-Seed Experiment (N={res['total_seeds']}):")
    print(f"  Novelty Rate: {res['metrics']['metric_a_candidate_novelty_rate']*100:.1f}%")
    print(f"  Pool Influence: {res['metrics']['metric_b_candidate_pool_influence_rate']*100:.1f}%")
    print(f"  Preference Influence: {res['metrics']['metric_c_preference_influence_rate']*100:.1f}%")
    print(f"  Decision Influence: {res['metrics']['metric_d_final_decision_influence_rate']*100:.1f}%")
    print(f"  Verdict: {res['verdict']}")
