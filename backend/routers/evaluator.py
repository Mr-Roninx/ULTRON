from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from evaluator.replay import replay_engine
from memory.episodic import memory_store

router = APIRouter(prefix="/evaluator", tags=["Evaluator"])

@router.post("/replay/{customer_id}")
def run_replay(customer_id: str, max_risk: float = 1.0, authority: str = "AUTONOMOUS"):
    """Runs the counterfactual evaluator on all past memories for this customer."""
    try:
        results = replay_engine.run_replay_suite(customer_id, max_risk, authority)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memories/{customer_id}")
def get_customer_memories(customer_id: str):
    mems = [m for m in memory_store.memories if m.customer_id == customer_id]
    return [m.model_dump() for m in mems]
