import json
from typing import Dict, Any, List, Optional
from memory.episodic import memory_store
from backend.benchmark.firewall import firewall
from backend.llm.prompts import prompts
from simulator.clock import clock

class ContextBuilder:
    """
    Constructs bounded, future-safe, minimal token context for LLM reasoning.
    Reduces latency by eliminating redundant logs, raw database rows, and future lookaheads.
    """
    def __init__(self, max_context_chars: int = 2500):
        self.max_context_chars = max_context_chars

    def build_observation_context(self, raw_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts strictly current observable state, sanitizing future leakage."""
        # Enforce temporal firewall
        firewall.sanitize_agent_context(raw_context)

        payment = raw_context.get("payment", {})
        diagnosis = raw_context.get("diagnosis", {})
        customer = raw_context.get("customer", {})
        mission = raw_context.get("mission", {})

        obs = {
            "simulation_time": clock.now(),
            "customer_id": customer.get("id") or raw_context.get("customer_id", "UNKNOWN"),
            "segment": customer.get("segment", "SMB"),
            "total_exposure": mission.get("total_exposure", payment.get("amount", 0.0)),
            "payment": {
                "id": payment.get("id"),
                "amount": payment.get("amount", 0.0),
                "rail": payment.get("rail", "UNKNOWN"),
                "gateway_id": payment.get("gateway_id", "GATEWAY_A"),
                "failure_code": payment.get("failure_code") or payment.get("iso_code", "UNKNOWN")
            },
            "diagnosis": {
                "primary_reason": diagnosis.get("primary_reason", "UNKNOWN_ERROR"),
                "failure_class": diagnosis.get("failure_class", "UNKNOWN"),
                "recoverability": diagnosis.get("recoverability", 0.50),
                "retry_eligible": diagnosis.get("retry_eligible", True)
            }
        }
        return obs

    def build_memory_context(self, customer_id: str, failure_type: str, max_episodes: int = 3) -> str:
        """Retrieves bounded historical episodes without bloating the prompt."""
        mems = memory_store.retrieve(customer_id, failure_type)
        if not mems:
            return "None."
        
        # Take the most recent bounded episodes
        recent_mems = mems[-max_episodes:]
        lines = []
        for m in recent_mems:
            res_str = "SUCCESS" if (m.result in ["SUCCESS", "SETTLED", "RECOVERED"] or m.recovery_amount > 0) else "FAILED"
            lines.append(f"- Action: {m.action_taken} -> {res_str} (Rec: ₹{m.recovery_amount:.0f}, Err: {m.prediction_error:.1f})")
        return "\n".join(lines)

    def build_policy_context(self, customer_segment: str, max_risk: float) -> Dict[str, Any]:
        """Provides minimal operational boundaries to guide candidate proposals."""
        return {
            "customer_segment": customer_segment,
            "max_risk_threshold": max_risk,
            "discounts_authorized": (customer_segment == "B2B_ENTERPRISE"),
            "financial_mutations_allowed": False
        }

    def build_action_context(self, feasible_actions: List[str]) -> List[str]:
        """Lists allowed candidate tools."""
        return sorted(list(set(feasible_actions)))

    def build_optimized_prompt(
        self,
        raw_context: Dict[str, Any],
        feasible_actions: List[str],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Builds the complete token-optimized message sequence for LLM invocation.
        """
        obs = self.build_observation_context(raw_context)
        cust_id = obs["customer_id"]
        failure_type = obs["diagnosis"]["primary_reason"]
        
        memory_summary = self.build_memory_context(cust_id, failure_type)
        policy_bounds = self.build_policy_context(obs["segment"], raw_context.get("max_risk", 1.0))
        allowed_actions = self.build_action_context(feasible_actions)

        sys_p = system_prompt or prompts.BASE_SYSTEM_PROMPT

        user_content_dict = {
            "observable_state": obs,
            "policy_constraints": policy_bounds,
            "allowed_actions": allowed_actions,
            "recent_memory": memory_summary
        }

        user_content_json = json.dumps(user_content_dict, indent=None, separators=(",", ":"))

        # Truncate if exceeds bounds
        if len(user_content_json) > self.max_context_chars:
            user_content_json = user_content_json[:self.max_context_chars]

        return [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": f"State:\n{user_content_json}\n\nPropose structured AgentIntent JSON:"}
        ]

context_builder = ContextBuilder()
