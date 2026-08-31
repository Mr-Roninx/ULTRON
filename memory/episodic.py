from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from simulator.clock import clock

class EpisodeRecord(BaseModel):
    customer_id: str
    failure_type: str
    action_taken: str
    result: str
    recovery_amount: float
    timestamp: int
    mission_id: Optional[str] = None
    failure_class: Optional[str] = None
    expected_value: Optional[float] = None
    prediction_error: Optional[float] = None
    customer_response: Optional[str] = None
    outcome: Optional[str] = None

class EpisodicMemory:
    """
    Episodic memory store maintaining past longitudinal recovery interventions,
    prediction errors, and customer response outcomes.
    """
    def __init__(self):
        self.memories: List[EpisodeRecord] = []
        
    def reset(self):
        self.memories.clear()

    def clear(self):
        self.reset()

    def store(self, record: EpisodeRecord) -> None:
        self.memories.append(record)

    def store_episode(
        self,
        customer_id: str,
        failure_type: str,
        action_taken: str,
        prediction_error: float = 0.0,
        recovered: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        meta = metadata or {}
        rec = EpisodeRecord(
            customer_id=customer_id,
            failure_type=failure_type,
            action_taken=action_taken,
            result="SUCCESS" if recovered else "FAILED",
            recovery_amount=meta.get("recovery_amount", 5000.0 if recovered else 0.0),
            timestamp=clock.now(),
            prediction_error=prediction_error,
            customer_response=meta.get("response", "NONE"),
            outcome="RECOVERED" if recovered else "FAILED"
        )
        self.store(rec)
        
    def retrieve(self, customer_id: str, failure_type: Optional[str] = None) -> List[EpisodeRecord]:
        results = []
        for mem in self.memories:
            if mem.customer_id == customer_id:
                if failure_type is None or failure_type == "UNKNOWN" or mem.failure_type == failure_type:
                    results.append(mem)
        return results

    def get_episodes(self, customer_id: Optional[str] = None) -> List[EpisodeRecord]:
        if customer_id is None:
            return list(self.memories)
        return self.retrieve(customer_id)

    def get_action_effectiveness(self, customer_id: str, action_type: str) -> float:
        """
        Returns empirical recovery multiplier (0.2 to 1.5) based on historical episodes.
        """
        relevant = [
            m for m in self.memories 
            if m.customer_id == customer_id and (
                m.action_taken == action_type or 
                (action_type.startswith("RETRY") and m.action_taken.startswith("RETRY")) or
                (action_type in ["SEND_PAYMENT_LINK", "SEND_MESSAGE"] and m.action_taken in ["SEND_PAYMENT_LINK", "SEND_MESSAGE"])
            )
        ]
        if not relevant:
            return 1.0
        
        successes = sum(1 for m in relevant if m.recovery_amount > 0 or m.result in ["SUCCESS", "SETTLED", "RECOVERED"])
        success_rate = successes / len(relevant)
        
        # Scale to a multiplier: e.g. 0% success = 0.3x, 100% success = 1.3x
        return round(0.3 + (success_rate * 1.0), 3)

    def get_customer_summary(self, customer_id: str) -> Dict[str, Any]:
        cust_mems = [m for m in self.memories if m.customer_id == customer_id]
        if not cust_mems:
            return {"total_episodes": 0, "total_recovered": 0.0, "avg_prediction_error": 0.0}
        
        total_rec = sum(m.recovery_amount for m in cust_mems)
        errors = [m.prediction_error for m in cust_mems if m.prediction_error is not None]
        avg_err = sum(errors) / len(errors) if errors else 0.0

        return {
            "total_episodes": len(cust_mems),
            "total_recovered": round(total_rec, 2),
            "avg_prediction_error": round(avg_err, 2),
            "recent_actions": [m.action_taken for m in cust_mems[-5:]]
        }

memory_store = EpisodicMemory()
