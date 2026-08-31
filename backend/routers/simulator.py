from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from simulator.world import world
from simulator.clock import clock
from simulator.seed import seed_ananya_textiles

router = APIRouter(prefix="/simulator", tags=["Simulator"])

@router.post("/seed")
def seed_simulator():
    """Seeds the virtual world with the Ananya Textiles hackathon scenario."""
    try:
        seed_ananya_textiles()
        return {"status": "success", "message": "Simulator seeded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clock/advance")
def advance_clock(seconds: int):
    """Advances the virtual clock."""
    if seconds <= 0:
        raise HTTPException(status_code=400, detail="Seconds must be positive.")
    clock.advance(seconds)
    return {"current_time": clock.now()}

@router.get("/world")
def get_world_state() -> Dict[str, Any]:
    """Returns the entire state of the simulator world."""
    return {
        "customers": {k: v.model_dump() for k, v in world.customers.items()},
        "payments": {k: v.model_dump() for k, v in world.payments.items()},
        "invoices": {k: v.model_dump() for k, v in world.invoices.items()},
        "checkouts": {k: v.model_dump() for k, v in world.checkouts.items()},
        "recovery_actions": {k: v.model_dump() for k, v in world.recovery_actions.items()},
        "communications": {k: v.model_dump() for k, v in world.communications.items()},
        "time": clock.now()
    }

@router.get("/events")
def get_event_bus_history():
    from simulator.event_bus import event_bus
    return [e.model_dump() for e in event_bus.get_history()]
