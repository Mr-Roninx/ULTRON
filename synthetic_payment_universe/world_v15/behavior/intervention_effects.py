from typing import Dict, Any, Tuple
from pydantic import BaseModel

class NegativeInterventionEffect(BaseModel):
    fatigue_delta: float
    relationship_delta: float
    opt_out_triggered: bool = False
    churn_triggered: bool = False
    externality_cost: float = 0.0

class InterventionEffectsEngine:
    """
    Models realistic adverse consequences of unnecessary, aggressive, or mistimed interventions.
    """
    @staticmethod
    def evaluate_outreach_effect(
        action_type: str,
        channel: str,
        current_fatigue: float,
        is_natural_recovery: bool = False
    ) -> NegativeInterventionEffect:
        base_fatigue_deltas = {
            "EMAIL": 0.05,
            "SMS": 0.10,
            "WHATSAPP": 0.16,
            "VOICE": 0.35,
            "AGGRESSIVE_DUNNING": 0.45
        }
        f_delta = base_fatigue_deltas.get(channel.upper(), 0.10)
        if action_type == "AGGRESSIVE_DUNNING":
            f_delta = 0.45

        new_fatigue = min(1.0, current_fatigue + f_delta)
        rel_delta = -0.02
        opt_out = False
        churn = False
        cost = 0.0

        # If customer would have paid naturally, unnecessary outreach annoys them
        if is_natural_recovery:
            rel_delta -= 0.06
            cost += 45.0 # Unnecessary communication cost

        # High fatigue penalties
        if new_fatigue >= 0.85:
            opt_out = True
            rel_delta -= 0.15
            cost += 150.0 # Relationship damage cost
        if new_fatigue >= 0.92:
            churn = True
            rel_delta -= 0.30
            cost += 1200.0 # Customer acquisition replacement cost

        return NegativeInterventionEffect(
            fatigue_delta=round(f_delta, 3),
            relationship_delta=round(rel_delta, 3),
            opt_out_triggered=opt_out,
            churn_triggered=churn,
            externality_cost=round(cost, 2)
        )
