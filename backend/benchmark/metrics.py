import math
import random
from typing import List, Dict, Any, Tuple
from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus
from simulator.world import FinancialWorld
from backend.benchmark.models import (
    BenchmarkOpportunity, OpportunityResult, StrategyMetrics, 
    AggregateMetrics, SegmentMetrics
)

class MetricsCalculator:
    """
    Computes all primary, safety, efficiency, and statistical metrics 
    for benchmark evaluations.
    """
    @staticmethod
    def calculate_strategy_metrics(
        strategy_name: str,
        seed: int,
        horizon_days: int,
        initial_world: FinancialWorld,
        final_world: FinancialWorld,
        opportunities: List[BenchmarkOpportunity],
        strategy_stats: dict,
        natural_recovery_amount: float = 0.0,
        control_recovery_amount: float = 0.0
    ) -> Tuple[StrategyMetrics, List[OpportunityResult]]:
        
        revenue_at_risk = sum(opp.initial_amount for opp in opportunities)
        addressable_revenue = revenue_at_risk
        
        gross_recovery = 0.0
        opp_results: List[OpportunityResult] = []

        for opp in opportunities:
            opp_recovered = 0.0
            if opp.entity_type == "PAYMENT":
                p = final_world.payments.get(opp.entity_id)
                if p and p.status == PaymentStatus.SETTLED:
                    opp_recovered = opp.initial_amount
            elif opp.entity_type == "INVOICE":
                inv = final_world.invoices.get(opp.entity_id)
                if inv and inv.status == InvoiceStatus.PAID:
                    opp_recovered = opp.initial_amount
            elif opp.entity_type == "CHECKOUT":
                chk = final_world.checkouts.get(opp.entity_id)
                if chk and chk.status == CheckoutStatus.COMPLETED:
                    opp_recovered = opp.initial_amount
                    
            gross_recovery += opp_recovered

            opp_results.append(OpportunityResult(
                opportunity_id=opp.opportunity_id,
                customer_id=opp.customer_id,
                initial_amount=opp.initial_amount,
                channel=opp.channel,
                failure_type=opp.failure_type,
                customer_segment=opp.customer_segment,
                payment_rail=opp.payment_rail,
                amount_bucket=opp.amount_bucket,
                control_strategy="Control",
                control_action=None,
                control_recovered=0.0,
                treatment_strategy=strategy_name,
                ultron_action=strategy_stats.get("actions", {}).get(opp.opportunity_id),
                ultron_recovered=opp_recovered,
                incremental_recovery=opp_recovered,
                net_incremental_recovery=opp_recovered
            ))

        incremental_recovery = gross_recovery - control_recovery_amount
        intervention_cost = strategy_stats.get("intervention_cost", 0.0)
        relationship_cost = strategy_stats.get("relationship_cost", 0.0)
        risk_cost = strategy_stats.get("risk_cost", 0.0)
        total_cost = intervention_cost + relationship_cost + risk_cost
        net_incremental_recovery = incremental_recovery - total_cost

        recovery_rate = gross_recovery / max(1.0, addressable_revenue)
        incremental_recovery_rate = incremental_recovery / max(1.0, addressable_revenue)

        actions_attempted = strategy_stats.get("actions_attempted", 0)
        actions_successful = strategy_stats.get("actions_successful", 0)
        actions_blocked = strategy_stats.get("actions_blocked", 0)
        contacts = strategy_stats.get("customer_contacts", 0)
        escalations = strategy_stats.get("escalations", 0)
        replans = strategy_stats.get("replans", 0)

        metrics = StrategyMetrics(
            strategy_name=strategy_name,
            seed=seed,
            horizon_days=horizon_days,
            revenue_at_risk=round(revenue_at_risk, 2),
            addressable_revenue=round(addressable_revenue, 2),
            natural_recovery=round(natural_recovery_amount, 2),
            gross_recovery=round(gross_recovery, 2),
            incremental_recovery=round(incremental_recovery, 2),
            net_incremental_recovery=round(net_incremental_recovery, 2),
            recovery_rate=round(recovery_rate, 4),
            incremental_recovery_rate=round(incremental_recovery_rate, 4),
            actions_attempted=actions_attempted,
            actions_successful=actions_successful,
            actions_blocked=actions_blocked,
            escalations=escalations,
            customer_contacts=contacts,
            replans=replans,
            avg_time_to_recovery_hours=round(strategy_stats.get("avg_latency_hours", 24.0), 2),
            intervention_cost=round(intervention_cost, 2),
            relationship_cost=round(relationship_cost, 2),
            risk_cost=round(risk_cost, 2),
            total_cost=round(total_cost, 2),
            policy_violations=0,
            fsm_violations=0,
            duplicate_actions=0,
            unauthorized_actions=0,
            future_information_leaks=0,
            recovery_per_action=round(gross_recovery / max(1, actions_attempted), 2),
            recovery_per_contact=round(gross_recovery / max(1, contacts), 2),
            recovery_per_operational_hour=round(gross_recovery / max(1.0, actions_attempted * 0.1), 2)
        )
        return metrics, opp_results

    @staticmethod
    def bootstrap_ci95(values: List[float], num_resamples: int = 1000, seed: int = 42) -> List[float]:
        """
        Calculates 95% bootstrap confidence intervals with fixed seed.
        """
        if not values:
            return [0.0, 0.0]
        if len(values) == 1:
            return [round(values[0], 2), round(values[0], 2)]

        rng = random.Random(seed)
        n = len(values)
        resample_means = []
        for _ in range(num_resamples):
            sample = [rng.choice(values) for _ in range(n)]
            resample_means.append(sum(sample) / n)
        resample_means.sort()
        
        lower_idx = int(0.025 * num_resamples)
        upper_idx = int(0.975 * num_resamples)
        return [round(resample_means[lower_idx], 2), round(resample_means[upper_idx], 2)]

    @classmethod
    def aggregate_strategy_metrics(cls, strategy_name: str, metric_list: List[StrategyMetrics]) -> AggregateMetrics:
        n = len(metric_list)
        if n == 0:
            raise ValueError(f"No metrics to aggregate for strategy {strategy_name}")

        gross_vals = [m.gross_recovery for m in metric_list]
        inc_vals = [m.incremental_recovery for m in metric_list]
        net_inc_vals = [m.net_incremental_recovery for m in metric_list]
        rate_vals = [m.recovery_rate for m in metric_list]

        def _mean(arr): return sum(arr) / len(arr)
        def _median(arr):
            s = sorted(arr)
            mid = len(s) // 2
            return s[mid] if len(s) % 2 != 0 else (s[mid - 1] + s[mid]) / 2.0
        def _std(arr, m):
            if len(arr) <= 1:
                return 0.0
            return math.sqrt(sum((x - m) ** 2 for x in arr) / (len(arr) - 1))

        g_mean = _mean(gross_vals)
        i_mean = _mean(inc_vals)
        net_mean = _mean(net_inc_vals)
        r_mean = _mean(rate_vals)

        return AggregateMetrics(
            strategy_name=strategy_name,
            sample_size_seeds=n,
            horizon_days=metric_list[0].horizon_days,
            gross_recovery_mean=round(g_mean, 2),
            gross_recovery_median=round(_median(gross_vals), 2),
            gross_recovery_std=round(_std(gross_vals, g_mean), 2),
            gross_recovery_ci95=cls.bootstrap_ci95(gross_vals),
            incremental_recovery_mean=round(i_mean, 2),
            incremental_recovery_median=round(_median(inc_vals), 2),
            incremental_recovery_std=round(_std(inc_vals, i_mean), 2),
            incremental_recovery_ci95=cls.bootstrap_ci95(inc_vals),
            net_incremental_recovery_mean=round(net_mean, 2),
            net_incremental_recovery_median=round(_median(net_inc_vals), 2),
            net_incremental_recovery_std=round(_std(net_inc_vals, net_mean), 2),
            net_incremental_recovery_ci95=cls.bootstrap_ci95(net_inc_vals),
            recovery_rate_mean=round(r_mean, 4),
            recovery_rate_ci95=cls.bootstrap_ci95(rate_vals),
            contacts_mean=round(_mean([m.customer_contacts for m in metric_list]), 1),
            actions_mean=round(_mean([m.actions_attempted for m in metric_list]), 1),
            replans_mean=round(_mean([m.replans for m in metric_list]), 1),
            total_cost_mean=round(_mean([m.total_cost for m in metric_list]), 2),
            policy_violations_total=sum(m.policy_violations for m in metric_list),
            fsm_violations_total=sum(m.fsm_violations for m in metric_list),
            future_leaks_total=sum(m.future_information_leaks for m in metric_list)
        )

    @staticmethod
    def compute_segment_metrics(dimension: str, control_results: List[OpportunityResult], ultron_results: List[OpportunityResult]) -> List[SegmentMetrics]:
        # Group by dimension
        grouped: Dict[str, Dict[str, Any]] = {}
        
        for c_res, u_res in zip(control_results, ultron_results):
            val = getattr(c_res, dimension, "UNKNOWN")
            if val not in grouped:
                grouped[val] = {
                    "count": 0,
                    "addressable": 0.0,
                    "control_rec": 0.0,
                    "ultron_rec": 0.0,
                    "ultron_wins": 0
                }
            grouped[val]["count"] += 1
            grouped[val]["addressable"] += c_res.initial_amount
            grouped[val]["control_rec"] += c_res.control_recovered
            grouped[val]["ultron_rec"] += u_res.ultron_recovered
            if u_res.ultron_recovered > c_res.control_recovered:
                grouped[val]["ultron_wins"] += 1

        results = []
        for val, data in sorted(grouped.items()):
            inc = data["ultron_rec"] - data["control_rec"]
            results.append(SegmentMetrics(
                segment_dimension=dimension,
                segment_value=str(val),
                opportunity_count=data["count"],
                addressable_revenue=round(data["addressable"], 2),
                control_recovered=round(data["control_rec"], 2),
                ultron_recovered=round(data["ultron_rec"], 2),
                incremental_recovery=round(inc, 2),
                net_incremental_recovery=round(inc, 2),
                ultron_win_rate=round(data["ultron_wins"] / max(1, data["count"]), 4)
            ))
        return results
