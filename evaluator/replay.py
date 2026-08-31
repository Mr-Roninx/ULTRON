from typing import List, Dict, Any
from memory.episodic import memory_store, EpisodeRecord
from evaluator.counterfactual import counterfactual_evaluator
from backend.agent.schemas import AgentIntent

class ReplayEngine:
    def __init__(self):
        pass

    def run_replay_suite(self, customer_id: str, max_risk: float, authority: str) -> List[Dict[str, Any]]:
        """
        Loads all past episodic memories for a customer and evaluates 
        counterfactual regret for the actions taken historically.
        This allows the system to learn if it made suboptimal choices.
        """
        # We retrieve all memories (using empty failure_type to get all, but currently memory_store requires exact match)
        # For replay, let's just inspect all memories for the customer.
        customer_memories = [m for m in memory_store.memories if m.customer_id == customer_id]
        
        results = []
        for mem in customer_memories:
            # Reconstruct the intent that was taken
            intent = AgentIntent(
                action_type=mem.action_taken,
                reasoning="Historical replay reconstruction",
                expected_yield=mem.recovery_amount,
                payload={}
            )
            
            # Note: In a real system, the exact world state at the time of the memory 
            # would be loaded. For this MVP, we evaluate against the CURRENT world state 
            # to see if taking that action NOW would cause regret.
            evaluation = counterfactual_evaluator.calculate_regret(customer_id, intent, max_risk, authority)
            
            results.append({
                "memory_timestamp": mem.timestamp,
                "historical_action": mem.action_taken,
                "evaluation": evaluation
            })
            
        return results

replay_engine = ReplayEngine()
