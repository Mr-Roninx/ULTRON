import os
from typing import Tuple
from backend.providers.errors import EnvironmentSafetyError

class RazorpayEnvironmentGuard:
    """
    Dedicated guard ensuring Razorpay execution strictly targets TEST/SANDBOX mode.
    """
    def __init__(self):
        self.production_enabled: bool = False

    def validate_execution(self, is_live_attempt: bool = False) -> Tuple[bool, str]:
        # 1. Reject live/production attempts
        if is_live_attempt or self.production_enabled:
            return False, "EXECUTION_BLOCKED: Production live mode is strictly DISABLED for Razorpay in v5.0."

        # 2. Validate environment mode
        key_id = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock")
        if key_id.startswith("rzp_live_"):
            return False, "EXECUTION_BLOCKED: Detected LIVE Razorpay credentials. ULTRON v5 operates in TEST mode only."

        return True, "EXECUTION_PERMITTED (RAZORPAY_TEST)"

razorpay_guard = RazorpayEnvironmentGuard()
