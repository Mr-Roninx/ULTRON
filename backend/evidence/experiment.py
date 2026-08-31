import argparse
import sys
import os
import time
from typing import Dict, Any

from backend.evidence.models import ExperimentIdentity
from backend.evidence.instrumentation import create_experiment_identity
from backend.evidence.llm_evidence import verify_live_llm_path, measure_llm_candidate_influence
from backend.evidence.mechanism_evidence import (
    run_payment_intelligence_ablation,
    run_memory_influence_experiment,
    run_chaos_replanning_experiment
)
from backend.evidence.economic_evidence import run_economic_lift_benchmark
from backend.evidence.statistical_analysis import (
    calculate_paired_statistics,
    generate_mechanism_contribution_table
)
from backend.evidence.anti_gaming import audit_repository_for_gaming
from backend.evidence.report_generator import generate_phase14_reports

def run_all_experiments(
    output_dir: str = "results/phase14",
    docs_dir: str = "docs",
    seeds_count: int = 25
) -> int:
    print("=" * 60)
    print("ULTRON v3.6 — PHASE 14 MASTER EVIDENCE & REALITY AUDIT")
    print("=" * 60)
    start_time = time.time()

    # 1. Manifest creation
    manifest = {
        "experiment_id": "EXP_PHASE_14_MASTER",
        "timestamp": time.time(),
        "evaluation_seeds": list(range(101, 101 + seeds_count)),
        "horizon_days": 14,
        "llm_provider": os.environ.get("ULTRON_LLM_PROVIDER", "auto"),
        "version": "3.6"
    }
    print(f"\n[1/8] Manifest initialized for {seeds_count} evaluation seeds.")

    # 2. Experiment 1: Live LLM Verification
    print("[2/8] Executing Experiment 1: Live LLM Path Verification...")
    llm_ev = verify_live_llm_path("exp_llm_live")
    print(f"      Provider: {llm_ev.provider} | Latency: {llm_ev.latency_ms}ms | Fallback: {llm_ev.fallback_used}")

    # 3. Experiment 2: LLM Candidate Influence
    print("[3/8] Executing Experiment 2: LLM Candidate Influence...")
    llm_influence = measure_llm_candidate_influence()
    novelty = sum(r.candidate_novelty_rate for r in llm_influence) / max(1, len(llm_influence))
    influence = sum(1 for r in llm_influence if r.altered_decision) / max(1, len(llm_influence))
    print(f"      Novelty Rate: {novelty*100:.1f}% | Decision Influence Rate: {influence*100:.1f}%")

    # 4. Experiment 3: Payment Intelligence Ablation
    print("[4/8] Executing Experiment 3: Payment Intelligence Ablation...")
    pi_ablation = run_payment_intelligence_ablation()
    pi_diffs = sum(1 for r in pi_ablation if r.decision_differed)
    print(f"      Completed 6 scenarios. Decisions Differed: {pi_diffs}/6")

    # 5. Experiment 4 & 5: Memory & Chaos Replanning
    print("[5/8] Executing Experiments 4 & 5: Episodic Memory & Chaos Replanning...")
    mem_result = run_memory_influence_experiment()
    replan_result = run_chaos_replanning_experiment()
    print(f"      Memory Influenced: {mem_result.memory_influenced} | Chaos Plan Invalidated: {replan_result.plan_invalidated} (Action Changed: {replan_result.action_changed})")

    # 6. Experiment 6: Paired Economic Lift
    print(f"[6/8] Executing Experiment 6: Paired Economic Lift ({seeds_count} Seeds)...")
    eval_seeds = list(range(101, 101 + seeds_count))
    economic_results, ablation_rows = run_economic_lift_benchmark(seeds=eval_seeds)

    diffs_rule = [r.paired_incremental_vs_rule_based for r in economic_results]
    diffs_fixed = [r.paired_incremental_vs_fixed_retry for r in economic_results]

    stats_rule = calculate_paired_statistics(diffs_rule)
    stats_fixed = calculate_paired_statistics(diffs_fixed)
    mech_table = generate_mechanism_contribution_table(ablation_rows)

    print(f"      Mean Incremental vs Rule-Based: INR {stats_rule.mean:,.2f} (95% CI: [INR {stats_rule.ci_95_lower:,.2f}, INR {stats_rule.ci_95_upper:,.2f}])")
    print(f"      Verdict: {stats_rule.verdict.value}")

    # 7. Anti-Gaming Code Audit
    print("[7/8] Executing Anti-Gaming Codebase Audit...")
    anti_gaming = audit_repository_for_gaming()
    print(f"      Scanned {anti_gaming['total_files_scanned']} files. Gaming Detected: {anti_gaming['gaming_detected']}")

    # 8. Report Compilation
    print("[8/8] Compiling JSON Artifacts and Markdown Reports...")
    generate_phase14_reports(
        output_dir=output_dir,
        docs_dir=docs_dir,
        manifest=manifest,
        llm_ev=llm_ev,
        llm_influence=llm_influence,
        pi_ablation=pi_ablation,
        mem_result=mem_result,
        replan_result=replan_result,
        economic_results=economic_results,
        ablation_rows=ablation_rows,
        stats_fixed=stats_fixed,
        stats_rule=stats_rule,
        mech_table=mech_table,
        anti_gaming=anti_gaming
    )

    duration = time.time() - start_time
    print(f"\nPhase 14 Master Audit completed successfully in {duration:.2f}s.")
    print(f"Artifacts written to `{output_dir}/` and `{docs_dir}/`.")
    return 1 if anti_gaming["gaming_detected"] else 0

def main():
    parser = argparse.ArgumentParser(description="ULTRON v3.6 Phase 14 Master Evidence Runner")
    parser.add_argument("--all", action="store_true", help="Execute complete Phase 14 master audit")
    parser.add_argument("--output-dir", type=str, default="results/phase14", help="Output directory for JSON artifacts")
    parser.add_argument("--docs-dir", type=str, default="docs", help="Documentation directory")
    parser.add_argument("--seeds", type=int, default=25, help="Number of evaluation seeds")
    args = parser.parse_args()

    exit_code = run_all_experiments(
        output_dir=args.output_dir,
        docs_dir=args.docs_dir,
        seeds_count=args.seeds
    )
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
