from backend.agent.state_machine import AgentStateMachine, AgentPhase
from backend.agent.circuit_breakers import circuit_breaker
from backend.agent.schemas import AgentIntent
from backend.agent.observation import observer
from memory.episodic import memory_store, EpisodeRecord
from backend.tools.registry import registry
from backend.tools.investigation import investigation_tools
from backend.mission.mission_tools import mission_tools
from backend.mission.mission_state import RevenueMissionState
from backend.payment_intelligence.payment_diagnosis import payment_diagnosis_engine
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.interference.interference_graph import interference_graph
from backend.economics.relationship import relationship_model
from backend.payment_simulator.outcome_model import outcome_model
from simulator.clock import clock
from simulator.world import world
from backend.llm.provider import LLMProvider, MockProvider
from backend.llm.context import context_manager
from backend.llm.context_builder import context_builder
from backend.agent.action_registry import action_registry
from backend.audit.trace_graph import trace_graph_engine
from backend.llm.functions import schema_generator
from backend.llm.prompts import prompts
from backend.agent.mission import AgentMission, MissionState, WakeReason
from backend.agent.schemas import Plan, PlanStatus, ActionScore
from backend.simulation.temporal_events import WakeupEvent
from backend.agent.telemetry import telemetry

class AgentLoop:
    def __init__(self, customer_id: str, mission_id: str, max_risk: float = 1.0, authority: str = "AUTONOMOUS", llm_provider: LLMProvider = None):
        self.customer_id = customer_id
        self.mission_id = mission_id
        self.max_risk = max_risk
        self.authority = authority
        self.fsm = AgentStateMachine(initial=AgentPhase.OBSERVE)
        self.llm = llm_provider or MockProvider()
        
        self.iteration_count = 0
        self.replan_count = 0
        self.identical_failures = 0
        self.llm_invocation_count = 0
        
        self.context = {}
        self.feasible_actions = []
        self.chosen_intent = None
        self.execution_result = None
        self.last_failure_type = None
        self.last_failure_class = None

        self.mission = AgentMission(
            mission_id=mission_id,
            customer_id=customer_id
        )
        trace_graph_engine.start_trace(mission_id=mission_id, customer_id=customer_id)

    def wake(self, event=None):
        self.mission.wake(event)
        # On wake, we restart the observation cycle to evaluate new state
        if self.fsm.current() == AgentPhase.WAIT:
            self.fsm.transition(AgentPhase.EVALUATE)
        elif self.fsm.current() != AgentPhase.COMPLETE:
            pass

    def tick(self):
        phase = self.fsm.current()
        
        if phase == AgentPhase.COMPLETE or phase == AgentPhase.ESCALATE:
            return phase

        if self.mission.state == MissionState.SLEEPING:
            return phase
            
        self.iteration_count += 1
        circuit_breaker.check(self.iteration_count, self.replan_count, self.identical_failures)

        if phase == AgentPhase.OBSERVE:
            self.context = investigation_tools.get_customer_context(self.customer_id)
            
            # Load active customer revenue mission
            revenue_mission = mission_tools.get_customer_mission(self.customer_id)
            self.context["mission"] = revenue_mission
            if revenue_mission:
                mission_tools.transition_mission_state(revenue_mission["mission_id"], RevenueMissionState.INVESTIGATING.value, "Agent observing world")

            telemetry.log_event(
                event_type="OBSERVE",
                mission_id=self.mission_id,
                payload={"customer_id": self.customer_id, "exposure": self.context.get("mission", {}).get("total_exposure", 0.0)}
            )
            self.fsm.transition(AgentPhase.INVESTIGATE)
            
        elif phase == AgentPhase.INVESTIGATE:
            # 1. Cross-opportunity interference
            interference = interference_graph.get_customer_exposure(self.customer_id)
            self.context["interference"] = interference
            
            # 2. Relationship State
            rel_state = relationship_model.get_relationship(self.customer_id)
            self.context["relationship_state"] = rel_state

            # 3. Find primary failed payment and diagnose failure
            failed_payments = investigation_tools.get_failed_payments(self.customer_id)
            if failed_payments:
                primary_payment = failed_payments[0]
                self.context["payment"] = primary_payment
                diag = investigation_tools.get_payment_diagnosis(primary_payment["id"], self.customer_id)
                self.context["diagnosis"] = diag
                self.last_failure_type = diag.get("primary_reason", "UNKNOWN_ERROR")
                self.last_failure_class = diag.get("failure_class", "UNKNOWN")
            else:
                self.context["diagnosis"] = {}
                self.last_failure_type = "UNKNOWN_ERROR"

            telemetry.log_event(
                event_type="INVESTIGATE",
                mission_id=self.mission_id,
                payload={"diagnosis": self.context.get("diagnosis"), "interference": interference}
            )
            self.fsm.transition(AgentPhase.HYPOTHESIZE)
            
        elif phase == AgentPhase.HYPOTHESIZE:
            telemetry.log_event(
                event_type="HYPOTHESIZE",
                mission_id=self.mission_id,
                payload={"failure_reason": self.last_failure_type, "customer_id": self.customer_id}
            )
            self.fsm.transition(AgentPhase.PLAN)
            
        elif phase == AgentPhase.PLAN:
            self.llm_invocation_count += 1
            inv_id = f"inv_{self.mission_id}_{self.llm_invocation_count}"

            # 1. Deterministic Action Generator
            self.feasible_actions = registry.decision.get_feasible_actions(self.customer_id, self.max_risk, self.authority)

            # 2. Format Bounded Context for LLM
            messages = context_builder.build_optimized_prompt(self.context, self.feasible_actions)
            schemas = schema_generator.get_tool_schemas([])
            
            # 3. LLM REASONER -> AgentIntent
            self.chosen_intent = self.llm.generate_intent(messages, schemas)
            
            # 4. Action Registry Filter: strictly reject unauthorized / unknown mutations
            cust_segment = self.context.get("customer", {}).get("segment", "SMB")
            raw_candidates = self.chosen_intent.candidate_actions or ([self.chosen_intent.action_type] if self.chosen_intent.action_type else [])
            if self.chosen_intent.preferred_action and self.chosen_intent.preferred_action not in raw_candidates:
                raw_candidates.append(self.chosen_intent.preferred_action)

            valid_llm_candidates, rejected_candidates = action_registry.reject_unauthorized_proposals(raw_candidates, cust_segment)
            llm_candidates = valid_llm_candidates

            if self.chosen_intent.action_type and self.chosen_intent.action_type not in self.feasible_actions and not any(a in self.feasible_actions for a in llm_candidates):
                self.fsm.transition(AgentPhase.FEASIBILITY_CHECK)
                return self.fsm.current()

            union_actions = list(set(llm_candidates + self.feasible_actions))
            
            # 5. Remove invalid actions (Policy / FSM / Financial constraints)
            filtered_actions = [a for a in union_actions if a in self.feasible_actions]
            
            # 6. Rank remaining actions deterministically
            from backend.agent.action_ranker import rank_actions
            candidate_scores = rank_actions(filtered_actions, self.context)
            if not candidate_scores:
                 self.fsm.transition(AgentPhase.REPLAN)
                 return self.fsm.current()

            best_action = candidate_scores[0]
            
            # Record preference differential
            llm_pref = self.chosen_intent.preferred_action
            det_pref = best_action.action
            
            telemetry.log_decision_differential(
                mission_id=self.mission_id,
                llm_preferred=llm_pref,
                deterministic_selected=det_pref,
                candidate_scores=[s.model_dump() for s in candidate_scores]
            )

            # Record in Trace Graph Engine
            from backend.llm.performance import llm_performance_controller
            latest_perf = llm_performance_controller.history[-1] if llm_performance_controller.history else None
            p_name = latest_perf.provider if latest_perf else "LLMRouter"
            m_name = latest_perf.model if latest_perf else "Qwen3.8-2.4T"
            lat_ms = latest_perf.latency_ms if latest_perf else 0.0
            fb_used = latest_perf.fallback_used if latest_perf else False

            trace_graph_engine.add_node(
                mission_id=self.mission_id,
                event_type="LLM_REASON",
                phase="PLAN",
                actor="LLM_ROUTER",
                llm_invocation_id=inv_id,
                provider=p_name,
                model=m_name,
                latency_ms=lat_ms,
                preferred_action=llm_pref,
                candidate_actions=llm_candidates,
                deterministic_action=det_pref,
                details={
                    "replan_count": self.replan_count,
                    "rejected_candidates": rejected_candidates,
                    "nev_selected": best_action.nev,
                    "fallback_used": fb_used
                }
            )

            # 7. ActionDecisionAuthority enforces selection
            self.chosen_intent.action_type = det_pref
            self.chosen_intent.expected_yield = best_action.expected_recovery
            
            plan = Plan(
                created_at=clock.now(),
                candidate_actions=candidate_scores,
                selected_action=det_pref,
                expected_value=best_action.expected_recovery,
                risk=best_action.risk_cost,
                authority=self.authority
            )
            self.mission.add_plan(plan)
            
            from backend.audit.ledger import audit_ledger
            audit_ledger.log(
                event_type="AGENT_INTENT_DECIDED",
                actor="ULTRON_AUTHORITY",
                payload={
                    "llm_preferred": llm_pref,
                    "action_type": det_pref, 
                    "expected_yield": best_action.expected_recovery, 
                    "reasoning": self.chosen_intent.reasoning
                },
                mission_id=self.mission_id
            )
            
            self.fsm.transition(AgentPhase.FEASIBILITY_CHECK)
            
        elif phase == AgentPhase.FEASIBILITY_CHECK:
            if not self.chosen_intent or self.chosen_intent.action_type not in self.feasible_actions:
                if self.mission.current_plan:
                    self.mission.current_plan.status = PlanStatus.INVALIDATED
                self.fsm.transition(AgentPhase.REPLAN)
            else:
                self.fsm.transition(AgentPhase.AUTHORITY_CHECK)
                
        elif phase == AgentPhase.AUTHORITY_CHECK:
            if self.mission.current_plan:
                self.mission.current_plan.status = PlanStatus.AUTHORIZED
            self.fsm.transition(AgentPhase.RISK_CHECK)
            
        elif phase == AgentPhase.RISK_CHECK:
            self.fsm.transition(AgentPhase.EXECUTE)
            
        elif phase == AgentPhase.EXECUTE:
            action_type = self.chosen_intent.action_type
            payload = self.chosen_intent.payload or {}
            payment_id = payload.get("payment_id") or self.context.get("payment", {}).get("id")
            
            if self.mission.current_plan:
                self.mission.current_plan.status = PlanStatus.EXECUTING

            # Execute chosen intent
            if action_type == "RECONCILE":
                self.execution_result = registry.execution.reconcile_payment(
                    self.mission_id, self.customer_id, payment_id, self.authority, self.max_risk
                )
            elif action_type in ["RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "RETRY_GATEWAY_C"]:
                target_gw = "GATEWAY_A"
                if "_" in action_type and action_type != "RETRY":
                    target_gw = action_type.replace("RETRY_", "")
                elif self.context.get("payment", {}).get("gateway_id"):
                    target_gw = self.context.get("payment", {}).get("gateway_id")

                self.execution_result = registry.execution.schedule_retry(
                    self.mission_id, self.customer_id, payment_id, payload.get("delay", 0), self.authority, self.max_risk
                )
                
                # In simulator, execute retry outcome
                if self.execution_result.success and payment_id:
                    status, details = outcome_model.process_payment_retry(payment_id, gateway_id=target_gw)

                delay = payload.get("delay", 0)
                if delay > 0 and self.execution_result.success:
                    self.mission.sleep(WakeReason.WAITING_FOR_RETRY)
                    clock.schedule(clock.now() + delay, WakeupEvent(agent_id=self.mission_id, scheduled_at=clock.now() + delay))

            elif action_type == "SWITCH_PERMITTED_RAIL":
                target_gw = payload.get("target_gateway", "GATEWAY_B")
                self.execution_result = registry.execution.switch_permitted_rail(
                    self.mission_id, self.customer_id, payload.get("target_rail", "CARD"), target_gw, self.authority, self.max_risk
                )
                if self.execution_result.success and payment_id:
                    outcome_model.process_payment_retry(payment_id, gateway_id=target_gw)

            elif action_type == "SEND_PAYMENT_LINK":
                self.execution_result = registry.execution.generate_payment_link(
                    self.mission_id, self.customer_id, payload.get("items", []), self.authority, self.max_risk
                )
                outcome_model.process_customer_communication(self.customer_id, "EMAIL", "PAYMENT_LINK")

            elif action_type in ["SEND_MESSAGE", "EMAIL", "SMS", "REQUEST_CUSTOMER_ACTION"]:
                channel = payload.get("channel", "EMAIL" if action_type == "EMAIL" else "SMS")
                self.execution_result = registry.execution.send_customer_message(
                    self.mission_id, self.customer_id, channel, payload.get("message_type", "REMINDER"), self.authority, self.max_risk
                )
                outcome_model.process_customer_communication(self.customer_id, channel, "MESSAGE")

            elif action_type in ["REGISTER_PTP", "PTP"]:
                self.execution_result = registry.execution.register_ptp(
                    self.mission_id, self.customer_id, payload.get("promise_date", clock.now() + 86400), self.authority, self.max_risk
                )
            elif action_type == "ESCALATE":
                self.execution_result = registry.execution.escalate_to_human(
                    self.mission_id, self.customer_id, payload.get("reason", "Customer exposure requires human intervention"), self.authority, self.max_risk
                )
            elif action_type == "WAIT":
                self.execution_result = type('Result', (), {'success': True, 'state_change': None, 'message': 'Waited'})()
            elif action_type == "STOP":
                if self.mission.current_plan:
                    self.mission.current_plan.status = PlanStatus.COMPLETED
                self.fsm.transition(AgentPhase.COMPLETE)
                return self.fsm.current()
            else:
                self.execution_result = type('Result', (), {'success': False, 'message': 'Unknown action', 'state_change': None})()

            if self.execution_result is None:
                self.execution_result = type('Result', (), {'success': False, 'message': 'Execution returned None', 'state_change': None})()

            from evaluator.counterfactual import counterfactual_evaluator
            try:
                regret_calc = counterfactual_evaluator.calculate_regret(self.customer_id, self.chosen_intent, self.max_risk, self.authority)
                self.context["last_regret_evaluation"] = regret_calc
            except Exception:
                pass

            telemetry.log_event(
                event_type="EXECUTE",
                mission_id=self.mission_id,
                payload={"action_type": action_type, "success": self.execution_result.success}
            )

            if self.execution_result.success:
                self.identical_failures = 0
                self.fsm.transition(AgentPhase.WAIT)
            else:
                self.identical_failures += 1
                if self.mission.current_plan:
                    self.mission.current_plan.status = PlanStatus.FAILED
                self.fsm.transition(AgentPhase.EVALUATE)
                
        elif phase == AgentPhase.WAIT:
            if self.mission.state != MissionState.SLEEPING:
                if self.mission.current_plan and self.mission.current_plan.status == PlanStatus.EXECUTING:
                    self.mission.current_plan.status = PlanStatus.WAITING
                self.fsm.transition(AgentPhase.EVALUATE)
            
        elif phase == AgentPhase.EVALUATE:
            gw_id = self.context.get("payment", {}).get("gateway_id", "GATEWAY_A")
            gw_health = rail_health_engine.get_gateway_health(gw_id)
            is_retry_action = self.chosen_intent.action_type.startswith("RETRY")
            gateway_degraded = is_retry_action and (gw_health.success_probability < 0.50)

            actual_status = "FAILED" if (gateway_degraded or not self.execution_result.success) else "SETTLED"
            observed_yield = 0.0 if actual_status == "FAILED" else self.chosen_intent.expected_yield

            eval_result = observer.evaluate(
                self.chosen_intent.expected_yield, 
                observed_yield, 
                actual_status
            )
            
            if eval_result["requires_replan"]:
                if self.mission.current_plan:
                    self.mission.current_plan.status = PlanStatus.INVALIDATED
                telemetry.log_event(event_type="REPLAN", mission_id=self.mission_id, payload={"reason": "Observer requires replan"})
                self.fsm.transition(AgentPhase.REPLAN)
            else:
                self.fsm.transition(AgentPhase.LEARN)
                
        elif phase == AgentPhase.LEARN:
            actual_yield = self.chosen_intent.expected_yield if self.execution_result.success else 0.0
            prediction_error = actual_yield - self.chosen_intent.expected_yield
            
            record = EpisodeRecord(
                customer_id=self.customer_id,
                mission_id=self.mission_id,
                failure_type=self.last_failure_type or "UNKNOWN",
                failure_class=self.last_failure_class or "UNKNOWN",
                action_taken=self.chosen_intent.action_type,
                result=self.execution_result.state_change or "SUCCESS",
                recovery_amount=actual_yield,
                expected_value=self.chosen_intent.expected_yield,
                prediction_error=prediction_error,
                timestamp=clock.now()
            )
            
            memory_store.store(record)
            if self.mission.current_plan:
                self.mission.current_plan.status = PlanStatus.COMPLETED

            telemetry.log_event(
                event_type="LEARN",
                mission_id=self.mission_id,
                payload={"recovery_amount": actual_yield, "prediction_error": prediction_error}
            )
            trace_graph_engine.add_node(
                mission_id=self.mission_id,
                event_type="LEARN",
                phase="LEARN",
                details={"recovery_amount": actual_yield, "prediction_error": prediction_error}
            )
            trace_graph_engine.export_trace(mission_id=self.mission_id)
            self.fsm.transition(AgentPhase.COMPLETE)
            
        elif phase == AgentPhase.REPLAN:
            self.replan_count += 1
            circuit_breaker.check(self.iteration_count, self.replan_count, self.identical_failures)
            trace_graph_engine.add_node(
                mission_id=self.mission_id,
                event_type="REPLAN",
                phase="REPLAN",
                details={"replan_count": self.replan_count}
            )
            self.fsm.transition(AgentPhase.INVESTIGATE)

        return self.fsm.current()
