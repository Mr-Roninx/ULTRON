from typing import Dict, Any, List, Tuple, Optional
from backend.evidence.models import EconomicLiftResult, AblationMatrixRow
from backend.benchmark.runner import BenchmarkRunner

def run_economic_lift_benchmark(
    seeds: Optional[List[int]] = None,
    horizon_days: int = 14
) -> Tuple[List[EconomicLiftResult], List[AblationMatrixRow]]:
    """
    Executes Experiment 6: Paired Counterfactual Economic Lift Benchmark.
    Runs independent evaluation seeds across all baseline and ULTRON strategies.
    Computes strict paired counterfactual increments without lookahead leakage.
    """
    eval_seeds = seeds or list(range(101, 126)) # 25 independent evaluation seeds
    lift_results: List[EconomicLiftResult] = []
    ablation_rows: List[AblationMatrixRow] = []

    runner = BenchmarkRunner()

    for seed in eval_seeds:
        exp_res = runner.run_single_experiment(seed=seed, horizon_days=horizon_days)
        metrics = exp_res["metrics"]
        opportunities = exp_res["opportunities"]
        total_at_risk = sum(o.initial_amount for o in opportunities)

        no_action = metrics.get("NoAction")
        fixed_retry = metrics.get("FixedRetry")
        dunning = metrics.get("TraditionalDunning")
        rule_based = metrics.get("RuleBasedRecovery")
        ultron = metrics.get("FULL_ULTRON")

        rec_no_action = no_action.gross_recovery if no_action else 0.0
        rec_fixed_retry = fixed_retry.gross_recovery if fixed_retry else 0.0
        rec_dunning = dunning.gross_recovery if dunning else 0.0
        rec_rule_based = rule_based.gross_recovery if rule_based else 0.0
        rec_ultron = ultron.gross_recovery if ultron else 0.0

        # Paired differences
        paired_inc_fixed = rec_ultron - rec_fixed_retry
        paired_inc_rule = rec_ultron - rec_rule_based
        ultron_nev = ultron.net_incremental_recovery if ultron else (rec_ultron * 0.94)

        lift_results.append(EconomicLiftResult(
            seed=seed,
            total_at_risk=round(total_at_risk, 2),
            no_action_recovery=round(rec_no_action, 2),
            fixed_retry_recovery=round(rec_fixed_retry, 2),
            traditional_dunning_recovery=round(rec_dunning, 2),
            rule_based_recovery=round(rec_rule_based, 2),
            ultron_recovery=round(rec_ultron, 2),
            paired_incremental_vs_fixed_retry=round(paired_inc_fixed, 2),
            paired_incremental_vs_rule_based=round(paired_inc_rule, 2),
            ultron_nev=round(ultron_nev, 2),
            time_to_recovery=round(ultron.avg_time_to_recovery_hours / 24.0 if ultron else 6.0, 2)
        ))

        # Record rows for Ablation Matrix
        for strat_name, strat_m in metrics.items():
            if strat_name in ["FULL_ULTRON", "ULTRON_NO_PAYMENT_INTELLIGENCE", "ULTRON_NO_MEMORY", "ULTRON_NO_REPLANNING", "RuleBasedRecovery", "FixedRetry"]:
                ablation_rows.append(AblationMatrixRow(
                    configuration=strat_name,
                    seed=seed,
                    gross_recovery=round(strat_m.gross_recovery, 2),
                    incremental_recovery=round(strat_m.incremental_recovery, 2),
                    recovery_rate=round(strat_m.recovery_rate, 4),
                    net_expected_value=round(strat_m.net_incremental_recovery, 2),
                    replan_count=strat_m.replans,
                    memory_influenced="ULTRON" in strat_name and "NO_MEMORY" not in strat_name
                ))

    return lift_results, ablation_rows
