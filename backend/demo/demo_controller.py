import os
from typing import Dict, Any, Optional
from simulator.clock import clock
from backend.demo.demo_scenarios import DEMO_SCENARIO_MAP
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.agent.state_machine import AgentPhase
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.llm.provider import LLMRouter, HuggingFaceProvider, MockProvider
from backend.audit.trace_graph import trace_graph_engine

class DemoController:
    """
    Interactive Demo Controller executing judge-ready scenarios with live or mocked LLM reasoning.
    """
    def __init__(self, scenario_id: str = "DEMO_04_GATEWAY_CHAOS", live_hf: bool = True):
        self.scenario_id = scenario_id
        self.live_hf = live_hf
        self.loop: Optional[AgentLoop] = None
        self.meta: Dict[str, Any] = {}

    def setup(self) -> Dict[str, Any]:
        setup_fn = DEMO_SCENARIO_MAP.get(self.scenario_id)
        if not setup_fn:
            raise ValueError(f"Unknown scenario ID: {self.scenario_id}. Available: {list(DEMO_SCENARIO_MAP.keys())}")
        
        self.meta = setup_fn()
        cust_id = self.meta["customer_id"]
        mission_id = f"msn_{self.scenario_id.lower()}"

        hf_token = os.environ.get("HF_TOKEN", "")
        fallback_intents = [
            AgentIntent(
                action_type="WAIT",
                candidate_actions=["WAIT", "RETRY_GATEWAY_A", "SEND_PAYMENT_LINK"],
                preferred_action="WAIT",
                reasoning="Demonstration intent: temporary issuer backoff (Fallback ladder active).",
                expected_yield=self.meta.get("amount", 24700.0),
                payload={}
            ),
            AgentIntent(
                action_type="SEND_PAYMENT_LINK",
                candidate_actions=["SEND_PAYMENT_LINK", "SWITCH_PERMITTED_RAIL", "ESCALATE"],
                preferred_action="SEND_PAYMENT_LINK",
                reasoning="Chaos adapted intent: Gateway degraded, switching to customer payment link.",
                expected_yield=self.meta.get("amount", 24700.0) * 0.85,
                payload={}
            )
        ]
        fallback_provider = MockProvider(fallback_intents)

        if self.live_hf and hf_token:
            primary_provider = HuggingFaceProvider(api_token=hf_token, timeout_seconds=6.0)
            provider = LLMRouter(primary=primary_provider, fallback=fallback_provider)
        else:
            provider = fallback_provider

        self.loop = AgentLoop(
            customer_id=cust_id,
            mission_id=mission_id,
            max_risk=1.0,
            authority="AUTONOMOUS",
            llm_provider=provider
        )
        return self.meta

    def run_to_wait(self) -> Dict[str, Any]:
        """Runs the agent through initial observation, LLM reasoning, NEV ranking, and execution into WAIT."""
        if not self.loop:
            self.setup()

        for _ in range(8):
            curr = self.loop.fsm.current()
            if curr == AgentPhase.WAIT:
                break
            self.loop.tick()

        return {
            "phase": self.loop.fsm.current().value,
            "chosen_action": self.loop.chosen_intent.action_type if self.loop.chosen_intent else "UNKNOWN",
            "llm_preferred": self.loop.chosen_intent.preferred_action if self.loop.chosen_intent else "UNKNOWN",
            "llm_invocations": self.loop.llm_invocation_count,
            "nev": self.loop.chosen_intent.expected_yield if self.loop.chosen_intent else 0.0
        }

    def inject_gateway_chaos(self, gateway_id: str = "GATEWAY_A", degraded_health: float = 0.10):
        """Simulates real-world mid-flight gateway degradation at T+2h."""
        clock.advance(7200) # +2 hours
        rail_health_engine.update_gateway_health(gateway_id, success_probability=degraded_health, latency_ms=4500.0)
        if self.loop:
            trace_graph_engine.add_node(
                mission_id=self.loop.mission_id,
                event_type="CHAOS_DEGRADATION",
                phase="WAIT",
                actor="ENVIRONMENT",
                details={"gateway_id": gateway_id, "degraded_health": degraded_health}
            )

    def wake_and_replan(self) -> Dict[str, Any]:
        """Wakes agent, invalidates plan, and triggers LLM Invocation #2 to adapt strategy."""
        if not self.loop:
            return {"error": "Loop not initialized"}

        self.loop.wake()
        self.loop.tick() # EVALUATE -> REPLAN

        # Complete Replan cycle to LEARN / COMPLETE
        for _ in range(10):
            if self.loop.fsm.current() in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
                break
            self.loop.tick()

        trace_path = f"d:/Work Space/Project/Ultron/results/phase16/traces/demo_{self.scenario_id.lower()}.json"
        trace_graph_engine.export_trace(mission_id=self.loop.mission_id, filepath=trace_path)

        return {
            "final_phase": self.loop.fsm.current().value,
            "final_action": self.loop.chosen_intent.action_type if self.loop.chosen_intent else "UNKNOWN",
            "total_llm_invocations": self.loop.llm_invocation_count,
            "replan_count": self.loop.replan_count,
            "trace_artifact": trace_path
        }
