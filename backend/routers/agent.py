from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from simulator.models import Mission, MissionGoal, MissionConstraints, MissionStatus
from backend.agent.runtime import runtime
import uuid

router = APIRouter(prefix="/agent", tags=["Agent"])

class StartMissionRequest(BaseModel):
    customer_id: str
    target_recovery: float
    max_risk: float
    authority: str = "AUTONOMOUS"

@router.post("/mission/start")
def start_mission(req: StartMissionRequest):
    mission = Mission(
        mission_id=f"m_{str(uuid.uuid4())[:8]}",
        objective="Recover failed payment",
        starting_state={},
        goal=MissionGoal(type="RECOVER_REVENUE", target=req.target_recovery),
        deadline=0, # Use 0 or virtual clock time + delta
        constraints=MissionConstraints(max_contacts=3, max_discount=0.0, max_risk=req.max_risk),
        authority=req.authority
    )
    
    # In a full async web environment, we might run this in a background task
    # For the simulator UI, we can step the loop explicitly, but here we just start it.
    loop = runtime.start_mission(mission)
    
    return {"status": "success", "mission_id": mission.mission_id}

@router.post("/mission/{mission_id}/step")
def step_mission(mission_id: str):
    """Executes a single tick of the agent loop."""
    loop = runtime.active_loops.get(mission_id)
    if not loop:
        raise HTTPException(status_code=404, detail="Mission loop not found.")
        
    phase = loop.tick()
    
    return {
        "phase": phase.value,
        "iteration_count": loop.iteration_count,
        "chosen_intent": loop.chosen_intent.model_dump() if loop.chosen_intent else None,
        "execution_result": loop.execution_result.__dict__ if loop.execution_result else None
    }

@router.get("/mission/{mission_id}/context")
def get_agent_context(mission_id: str):
    loop = runtime.active_loops.get(mission_id)
    if not loop:
        raise HTTPException(status_code=404, detail="Mission loop not found.")
        
    return {
        "phase": loop.fsm.current().value,
        "context": loop.context,
        "feasible_actions": loop.feasible_actions,
        "replan_count": loop.replan_count
    }
