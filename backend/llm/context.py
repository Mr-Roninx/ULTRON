import json
from typing import Dict, Any, List
from memory.episodic import memory_store
from pydantic import BaseModel

class ContextManager:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, str]] = []

    def format_state(self, context_snapshot: Dict[str, Any], feasible_actions: List[str]) -> str:
        def custom_serializer(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        state_str = json.dumps({
            "snapshot": context_snapshot,
            "feasible_actions": feasible_actions
        }, indent=2, default=custom_serializer)
        return state_str
        
    def get_memories(self, customer_id: str, failure_type: str) -> str:
        mems = memory_store.retrieve(customer_id, failure_type)
        if not mems:
            return "No relevant past episodes found."
            
        mem_str = "Past Episodes:\n"
        for idx, m in enumerate(mems):
            mem_str += f"{idx+1}. Action: {m.action_taken}, Result: {m.result}, Recovery: {m.recovery_amount}\n"
        return mem_str

    def build_prompt(self, system_prompt: str, state: str, memories: str) -> List[Dict[str, str]]:
        # In a real system, we'd trim older messages to fit max_tokens
        return [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": memories},
            {"role": "user", "content": f"Current State:\n{state}\n\nWhat is your next intent?"}
        ]

context_manager = ContextManager()
