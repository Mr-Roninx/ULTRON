import os
from enum import Enum
from typing import Dict, Any, Tuple

class ResolvedEnvironment(str, Enum):
    SWU = "SWU"
    MOCK = "MOCK"
    FIXTURE = "FIXTURE"
    RAZORPAY_TEST = "RAZORPAY_TEST"
    STRIPE_TEST = "STRIPE_TEST"
    ADYEN_TEST = "ADYEN_TEST"
    LIVE = "LIVE"

class EnvironmentTruthResolver:
    """
    Independently determines the execution environment based on real endpoints and configuration.
    """
    @staticmethod
    def resolve_environment(provider_name: str = "razorpay") -> Tuple[ResolvedEnvironment, str]:
        from backend.safety.production_gate import production_gate

        if production_gate.production_enabled:
            return ResolvedEnvironment.LIVE, "Live production execution is enabled (Caution)"

        # Check provider key presence
        p = provider_name.lower()
        if p == "razorpay":
            if os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET"):
                return ResolvedEnvironment.RAZORPAY_TEST, "Razorpay Test Sandbox active with configured credentials"
            return ResolvedEnvironment.FIXTURE, "Razorpay running in deterministic fixture/emulation mode"
        elif p == "stripe":
            if os.getenv("STRIPE_SECRET_KEY"):
                return ResolvedEnvironment.STRIPE_TEST, "Stripe Test Sandbox active with configured credentials"
            return ResolvedEnvironment.FIXTURE, "Stripe running in fixture mode (credentials not configured)"
        elif p == "adyen":
            if os.getenv("ADYEN_API_KEY"):
                return ResolvedEnvironment.ADYEN_TEST, "Adyen Test Sandbox active with configured credentials"
            return ResolvedEnvironment.FIXTURE, "Adyen running in fixture mode (credentials not configured)"

        return ResolvedEnvironment.SWU, "Synthetic Payment Universe simulation active"

environment_truth_resolver = EnvironmentTruthResolver()
