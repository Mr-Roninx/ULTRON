from enum import Enum

class AgentPhase(str, Enum):
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    HYPOTHESIZE = "HYPOTHESIZE"
    PLAN = "PLAN"
    FEASIBILITY_CHECK = "FEASIBILITY_CHECK"
    AUTHORITY_CHECK = "AUTHORITY_CHECK"
    RISK_CHECK = "RISK_CHECK"
    EXECUTE = "EXECUTE"
    WAIT = "WAIT"
    EVALUATE = "EVALUATE"
    LEARN = "LEARN"
    REPLAN = "REPLAN"
    ESCALATE = "ESCALATE"
    COMPLETE = "COMPLETE"

class InvalidAgentStateTransitionError(Exception):
    pass

class AgentStateMachine:
    VALID_TRANSITIONS = {
        AgentPhase.OBSERVE: {AgentPhase.INVESTIGATE, AgentPhase.COMPLETE},
        AgentPhase.INVESTIGATE: {AgentPhase.HYPOTHESIZE},
        AgentPhase.HYPOTHESIZE: {AgentPhase.PLAN},
        AgentPhase.PLAN: {AgentPhase.FEASIBILITY_CHECK},
        AgentPhase.FEASIBILITY_CHECK: {AgentPhase.AUTHORITY_CHECK, AgentPhase.REPLAN},
        AgentPhase.AUTHORITY_CHECK: {AgentPhase.RISK_CHECK, AgentPhase.REPLAN},
        AgentPhase.RISK_CHECK: {AgentPhase.EXECUTE, AgentPhase.REPLAN},
        AgentPhase.EXECUTE: {AgentPhase.WAIT, AgentPhase.EVALUATE, AgentPhase.COMPLETE},
        AgentPhase.WAIT: {AgentPhase.EVALUATE},
        AgentPhase.EVALUATE: {AgentPhase.LEARN, AgentPhase.REPLAN},
        AgentPhase.LEARN: {AgentPhase.REPLAN, AgentPhase.COMPLETE, AgentPhase.OBSERVE},
        AgentPhase.REPLAN: {AgentPhase.INVESTIGATE, AgentPhase.ESCALATE},
        AgentPhase.ESCALATE: set(),
        AgentPhase.COMPLETE: set()
    }
    
    def __init__(self, initial: AgentPhase = AgentPhase.OBSERVE):
        self._current = initial

    def transition(self, target: AgentPhase) -> None:
        if target not in self.VALID_TRANSITIONS.get(self._current, set()):
            raise InvalidAgentStateTransitionError(f"Cannot transition agent from {self._current} to {target}")
        self._current = target
        
    def current(self) -> AgentPhase:
        return self._current
