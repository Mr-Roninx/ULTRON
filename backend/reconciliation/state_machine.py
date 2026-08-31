from enum import Enum
from typing import Set, Dict

class ReconciliationState(str, Enum):
    MATCHED = "MATCHED"
    PENDING = "PENDING"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"
    RESOLVING = "RESOLVING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

class ReconciliationStateMachine:
    """
    Validates state transitions for financial reconciliation.
    """
    VALID_TRANSITIONS: Dict[ReconciliationState, Set[ReconciliationState]] = {
        ReconciliationState.PENDING: {ReconciliationState.MATCHED, ReconciliationState.MISMATCH, ReconciliationState.UNKNOWN},
        ReconciliationState.UNKNOWN: {ReconciliationState.RESOLVING, ReconciliationState.ESCALATED},
        ReconciliationState.MISMATCH: {ReconciliationState.RESOLVING, ReconciliationState.ESCALATED},
        ReconciliationState.RESOLVING: {ReconciliationState.RESOLVED, ReconciliationState.ESCALATED, ReconciliationState.MISMATCH},
        ReconciliationState.RESOLVED: set(),
        ReconciliationState.MATCHED: set(),
        ReconciliationState.ESCALATED: {ReconciliationState.RESOLVED}
    }

    @classmethod
    def validate_transition(cls, current: ReconciliationState, target: ReconciliationState) -> bool:
        allowed = cls.VALID_TRANSITIONS.get(current, set())
        return target in allowed
