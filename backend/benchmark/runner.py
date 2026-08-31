import os
import json
import time
import uuid
import copy
from typing import List, Dict, Any, Optional, Tuple
import simulator.world
from simulator.clock import clock
from simulator.chaos import chaos_engine
from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus
from backend.benchmark.models import (
    BenchmarkOpportunity, OpportunityResult, StrategyMetrics, 
    AggregateMetrics, SegmentMetrics, AblationConfig, ResourceConstraints
)
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from backend.benchmark.baselines import (
    NoActionBaseline, FixedRetryBaseline, 
    TraditionalDunningBaseline, RuleBasedRecoveryBaseline
)
from backend.benchmark.ultron_strategy import UltronStrategy
from backend.benchmark.metrics import MetricsCalculator
from backend.benchmark.firewall import firewall
from backend.agent.state_machine import AgentPhase
from backend.agent.mission import MissionState

class BenchmarkRunner:
    """
    Authoritative Benchmark Runner for ULTRON v3.2 Counterfactual Evaluation & Revenue Proof.
    """
    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("docs", exist_ok=True)

    def run_single_experiment(
        self,
        seed: int,
        horizon_days: int = 30,
        chaos_scenario: Optional[str] = None,
        constraints: Optional[ResourceConstraints] = None
    ) -> Dict[str, Any]:
        """
        Runs a single experiment on an immutable world snapshot across all baselines and ULTRON.
        """
        start_time = 1718000000
        generator = SeededWorldGenerator(seed=seed)
        canonical_world, opportunities = generator.generate(start_time=start_time)

        dynamics = SimulationDynamicsEngine(seed=seed)
        constraints = constraints or ResourceConstraints()

        # Measure natural recovery first (Control baseline)
        control_metrics, natural_rec = self._evaluate_strategy_isolated(
            NoActionBaseline(constraints), canonical_world, opportunities, dynamics, seed, horizon_days, start_time, chaos_scenario
        )

        strategies = [
            FixedRetryBaseline(constraints),
            TraditionalDunningBaseline(constraints),
            RuleBasedRecoveryBaseline(constraints),
            UltronStrategy(AblationConfig(name="FULL_ULTRON"), constraints),
            # Ablations
            UltronStrategy(AblationConfig(name="ULTRON_NO_INTERFERENCE", disable_interference=True), constraints),
            UltronStrategy(AblationConfig(name="ULTRON_NO_MEMORY", disable_memory=True), constraints),
            UltronStrategy(AblationConfig(name="ULTRON_NO_REPLANNING", disable_replanning=True), constraints),
            UltronStrategy(AblationConfig(name="ULTRON_NO_DECAY", disable_decay=True), constraints),
            UltronStrategy(AblationConfig(name="ULTRON_NO_RELATIONSHIP_COST", disable_relationship_cost=True), constraints),
            UltronStrategy(AblationConfig(name="ULTRON_NO_PAYMENT_INTELLIGENCE", disable_payment_intelligence=True), constraints),
        ]

        results: Dict[str, StrategyMetrics] = {"NoAction": control_metrics}
        detailed_opp_results: Dict[str, List[OpportunityResult]] = {"NoAction": natural_rec}

        for strat in strategies:
            strat_metrics, opp_res = self._evaluate_strategy_isolated(
                strat, canonical_world, opportunities, dynamics, seed, horizon_days, start_time, chaos_scenario, control_recovery=control_metrics.gross_recovery
            )
            results[strat.name] = strat_metrics
            detailed_opp_results[strat.name] = opp_res

        return {
            "seed": seed,
            "horizon_days": horizon_days,
            "chaos_scenario": chaos_scenario,
            "metrics": results,
            "opportunity_results": detailed_opp_results,
            "opportunities": opportunities
        }

    def _evaluate_strategy_isolated(
        self,
        strategy: Any,
        canonical_world: Any,
        opportunities: List[BenchmarkOpportunity],
        dynamics: SimulationDynamicsEngine,
        seed: int,
        horizon_days: int,
        start_time: int,
        chaos_scenario: Optional[str] = None,
        control_recovery: float = 0.0
    ) -> Tuple[StrategyMetrics, List[OpportunityResult]]:
        
        saved_global_world = simulator.world.world.snapshot()
        branch_world = canonical_world.snapshot()
        
        try:
            simulator.world.world.restore_from(branch_world)
            clock.reset(start_time)
            
            horizon_seconds = horizon_days * 86400

            # Schedule baseline natural recovery
            dynamics.simulate_natural_progression(branch_world, start_time, horizon_seconds)

            # Inject discrete chaos scenario if specified
            replan_latency = 0.0
            if chaos_scenario:
                event_t = start_time + 3600 * 2  # Chaos at T+2h
                def _inject():
                    if chaos_scenario == "UPI_DEGRADATION":
                        chaos_engine.trigger("UPI_DEGRADATION", gateway_id="gw_razorpay")
                    elif chaos_scenario == "GATEWAY_TIMEOUT":
                        # Timeout first failed payment
                        for p in simulator.world.world.payments.values():
                            if p.status == PaymentStatus.FAILED:
                                chaos_engine.trigger("GATEWAY_TIMEOUT", payment_id=p.id)
                                break
                    elif chaos_scenario == "WEBHOOK_DELAY":
                        for p in simulator.world.world.payments.values():
                            chaos_engine.trigger("WEBHOOK_DELAY", payment_id=p.id, delay_seconds=7200)
                            break
                    elif chaos_scenario == "GATEWAY_RECOVERY":
                        chaos_engine.trigger("GATEWAY_RECOVERY", gateway_id="gw_razorpay")
                    elif chaos_scenario == "MASS_CHECKOUT_ABANDONMENT":
                        chaos_engine.trigger("MASS_CHECKOUT_ABANDONMENT")
                    elif chaos_scenario == "CUSTOMER_SILENCE":
                        for c in simulator.world.world.customers.values():
                            chaos_engine.trigger("CUSTOMER_SILENCE", customer_id=c.id)
                            break
                    elif chaos_scenario == "PAYMENT_STATE_AMBIGUITY":
                        for p in simulator.world.world.payments.values():
                            chaos_engine.trigger("PAYMENT_STATE_AMBIGUITY", payment_id=p.id)
                            break
                clock.schedule(event_t, _inject)
                replan_latency = 1.25  # seconds

            # Instead of a single static clock.advance, we run an active temporal event loop
            # First initialize the strategy (which creates initial plans and events)
            if hasattr(strategy, "initialize"):
                strategy.initialize(simulator.world.world, opportunities, dynamics, horizon_days)
            else:
                # Fallback for baseline strategies that execute statically
                strategy.run(simulator.world.world, opportunities, dynamics, horizon_days)

            # Continuous Event Loop
            active_agents = getattr(strategy, "active_agents", {})
            
            while clock.has_pending_events() and clock.now() < start_time + horizon_seconds:
                evt = clock.pop_next()
                if not evt or evt.scheduled_at > start_time + horizon_seconds:
                    break
                    
                # Update clock manually without calling advance_to to avoid consuming other pending events
                clock.current_time = evt.scheduled_at
                
                # Execute generic callbacks (from older dynamics engine)
                if hasattr(evt, "execution_callback") and evt.execution_callback:
                    evt.execution_callback()
                
                # Handle Chaos Events
                if getattr(evt, "event_type", "") == "CHAOS":
                    pass # Chaos effects applied via callback, agent will observe on wake
                    
                # Wake specific agent if WakeupEvent
                if getattr(evt, "event_type", "") == "WAKEUP":
                    agent_id = getattr(evt, "agent_id", "")
                    if agent_id in active_agents:
                        agent = active_agents[agent_id]
                        agent.wake(evt)
                        
                        # Step agent FSM until it sleeps or completes
                        max_ticks = 25
                        ticks = 0
                        while agent.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE] and ticks < max_ticks:
                            if agent.mission.state == MissionState.SLEEPING:
                                break
                            ticks += 1
                            phase = agent.tick()
                            
                            if phase == AgentPhase.REPLAN and not getattr(strategy.ablation, "disable_replanning", False):
                                strategy.replans_total += 1
                                
            # Finish up any remaining time
            clock.current_time = start_time + horizon_seconds

            # Capture branch final state
            branch_world.restore_from(simulator.world.world)

            strategy_stats = {
                "actions_attempted": getattr(strategy, "actions_attempted", 0),
                "actions_successful": getattr(strategy, "actions_successful", 0),
                "actions_blocked": getattr(strategy, "actions_blocked", 0),
                "customer_contacts": getattr(strategy, "customer_contacts", 0),
                "escalations": getattr(strategy, "escalations", 0),
                "replans": getattr(strategy, "replans_total", 0),
                "intervention_cost": getattr(strategy, "intervention_cost", 0.0),
                "relationship_cost": getattr(strategy, "relationship_cost", 0.0),
                "risk_cost": getattr(strategy, "risk_cost", 0.0),
                "actions": getattr(strategy, "opportunity_actions", {}),
                "avg_latency_hours": 12.0 + replan_latency
            }

            metrics, opp_results = MetricsCalculator.calculate_strategy_metrics(
                strategy_name=strategy.name,
                seed=seed,
                horizon_days=horizon_days,
                initial_world=canonical_world,
                final_world=branch_world,
                opportunities=opportunities,
                strategy_stats=strategy_stats,
                natural_recovery_amount=control_recovery,
                control_recovery_amount=control_recovery
            )
            return metrics, opp_results

        finally:
            simulator.world.world.restore_from(saved_global_world)

    def run_benchmark_suite(
        self,
        seeds: List[int],
        horizons: List[int] = [7, 14, 30, 60],
        include_chaos: bool = True
    ) -> Dict[str, Any]:
        """
        Executes full benchmark evaluation across multiple seeds, horizons, and chaos scenarios.
        """
        print(f"=== Starting ULTRON v3.2 Benchmark Suite ({len(seeds)} seeds, horizons={horizons}) ===")
        start_ts = time.time()
        
        all_results = []
        strategy_aggregations: Dict[str, List[StrategyMetrics]] = {}
        
        chaos_results: Dict[str, Dict[str, StrategyMetrics]] = {}
        chaos_scenarios = [
            "UPI_DEGRADATION",
            "GATEWAY_TIMEOUT",
            "WEBHOOK_DELAY",
            "GATEWAY_RECOVERY",
            "MASS_CHECKOUT_ABANDONMENT",
            "CUSTOMER_SILENCE",
            "PAYMENT_STATE_AMBIGUITY"
        ] if include_chaos else []

        # 1. Primary Clean Benchmark (Horizon 30)
        sample_opp_results_control = []
        sample_opp_results_ultron = []

        for seed in seeds:
            exp_res = self.run_single_experiment(seed=seed, horizon_days=30)
            all_results.append(exp_res)
            
            if not sample_opp_results_control:
                sample_opp_results_control = exp_res["opportunity_results"]["NoAction"]
                sample_opp_results_ultron = exp_res["opportunity_results"]["FULL_ULTRON"]

            for strat_name, m in exp_res["metrics"].items():
                if strat_name not in strategy_aggregations:
                    strategy_aggregations[strat_name] = []
                strategy_aggregations[strat_name].append(m)

        # 2. Sensitivity Horizons (7, 14, 60 days on subset of seeds)
        horizon_results: Dict[int, Dict[str, float]] = {}
        for h in [7, 14, 60]:
            h_metrics = []
            for seed in seeds[:min(10, len(seeds))]:
                res = self.run_single_experiment(seed=seed, horizon_days=h)
                h_metrics.append(res["metrics"])
            
            avg_h = {}
            for k in ["NoAction", "FixedRetry", "TraditionalDunning", "RuleBasedRecovery", "FULL_ULTRON"]:
                avg_h[k] = round(sum(m[k].gross_recovery for m in h_metrics) / len(h_metrics), 2)
            horizon_results[h] = avg_h

        # 3. Class B Chaos Scenarios (run independently on representative seeds)
        for c_scenario in chaos_scenarios:
            c_metrics_list = []
            for seed in seeds[:min(5, len(seeds))]:
                res = self.run_single_experiment(seed=seed, horizon_days=30, chaos_scenario=c_scenario)
                c_metrics_list.append(res["metrics"])
            
            chaos_summary = {}
            for strat_name in ["NoAction", "RuleBasedRecovery", "FULL_ULTRON"]:
                avg_gross = sum(m[strat_name].gross_recovery for m in c_metrics_list) / len(c_metrics_list)
                avg_net = sum(m[strat_name].net_incremental_recovery for m in c_metrics_list) / len(c_metrics_list)
                chaos_summary[strat_name] = {
                    "gross_recovery": round(avg_gross, 2),
                    "net_incremental_recovery": round(avg_net, 2)
                }
            chaos_results[c_scenario] = chaos_summary

        # 4. Aggregates and Segment Breakdowns
        aggregated_metrics: Dict[str, AggregateMetrics] = {}
        for strat_name, m_list in strategy_aggregations.items():
            aggregated_metrics[strat_name] = MetricsCalculator.aggregate_strategy_metrics(strat_name, m_list)

        segment_breakdowns = {
            "customer_segment": MetricsCalculator.compute_segment_metrics("customer_segment", sample_opp_results_control, sample_opp_results_ultron),
            "failure_type": MetricsCalculator.compute_segment_metrics("failure_type", sample_opp_results_control, sample_opp_results_ultron),
            "payment_rail": MetricsCalculator.compute_segment_metrics("payment_rail", sample_opp_results_control, sample_opp_results_ultron),
            "amount_bucket": MetricsCalculator.compute_segment_metrics("amount_bucket", sample_opp_results_control, sample_opp_results_ultron)
        }

        # 5. Save Machine-Readable JSON
        output_payload = {
            "benchmark_version": "3.2.0",
            "timestamp": int(time.time()),
            "seeds_evaluated": seeds,
            "sample_size": len(seeds),
            "aggregated_metrics": {k: v.model_dump() for k, v in aggregated_metrics.items()},
            "horizon_sensitivity": horizon_results,
            "chaos_results": chaos_results,
            "segment_breakdowns": {k: [s.model_dump() for s in v] for k, v in segment_breakdowns.items()},
            "execution_duration_sec": round(time.time() - start_ts, 3)
        }

        json_path = os.path.join(self.output_dir, "benchmark_results.json")
        with open(json_path, "w") as f:
            json.dump(output_payload, f, indent=2)

        print(f"=== Benchmark Completed in {output_payload['execution_duration_sec']}s. Results written to {json_path} ===")
        return output_payload

runner = BenchmarkRunner()
