import os
from enum import Enum
from typing import Dict, Any, Tuple, Optional
from backend.providers.errors import EnvironmentSafetyError

class EnvironmentMode(str, Enum):
    SWU = "SWU"
    SHADOW = "SHADOW"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    SANDBOX_AUTONOMOUS = "SANDBOX_AUTONOMOUS"
    PRODUCTION_DISABLED = "PRODUCTION_DISABLED"
    PRODUCTION_LIVE = "PRODUCTION_LIVE"

class ProductionExecutionGate:
    """
    Absolute fail-closed gate ensuring real production money operations are never executed accidentally.
    """
    def __init__(self):
        self.production_enabled: bool = False # Strictly False by default in v5.0
        self.kill_switch_active: bool = False
        self.current_mode: EnvironmentMode = EnvironmentMode.SWU

    def set_environment(self, mode: EnvironmentMode):
        self.current_mode = mode

    def activate_kill_switch(self):
        self.kill_switch_active = True

    def clear_kill_switch(self):
        self.kill_switch_active = False

    def validate_execution(
        self,
        provider: str,
        action_type: str,
        amount_minor: int,
        is_live_request: bool = False
    ) -> Tuple[bool, str]:
        # 1. Kill Switch Check
        if self.kill_switch_active:
            return False, "EXECUTION_BLOCKED: Global kill switch is ACTIVE."

        # 2. Live / Production Check
        if is_live_request:
            if not self.production_enabled:
                return False, "EXECUTION_BLOCKED: Production execution is strictly DISABLED in v5.0."
            if self.current_mode != EnvironmentMode.PRODUCTION_LIVE:
                return False, f"EXECUTION_BLOCKED: Environment mode '{self.current_mode}' does not permit live transactions."

        # 3. Mode Rules
        if self.current_mode == EnvironmentMode.SHADOW:
            return False, "EXECUTION_BLOCKED: Running in SHADOW mode (only observations & recommendations permitted)."

        return True, "EXECUTION_PERMITTED"

production_gate = ProductionExecutionGate()
