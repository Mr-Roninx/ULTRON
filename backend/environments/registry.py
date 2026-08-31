from typing import Dict, Any, Optional
from backend.environments.environment import PaymentEnvironment
from backend.environments.synthetic import SyntheticWorldEnvironment
from backend.environments.real_provider import RealProviderEnvironment

class EnvironmentRegistry:
    """
    Registry for active execution environments in ULTRON.
    """
    def __init__(self):
        self._envs: Dict[str, PaymentEnvironment] = {
            "swu": SyntheticWorldEnvironment(),
            "razorpay": RealProviderEnvironment("razorpay")
        }
        self._active_env = "swu"

    def get_active_environment(self) -> PaymentEnvironment:
        return self._envs[self._active_env]

    def set_active_environment(self, name: str):
        key = name.lower()
        if key not in self._envs:
            raise ValueError(f"Unknown environment '{name}'")
        self._active_env = key

environment_registry = EnvironmentRegistry()
