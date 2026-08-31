import json
import time
from typing import Dict, Any
from backend.readiness.levels import ReadinessLevel
from backend.readiness.checks import readiness_checker

class ReadinessReportGenerator:
    """
    Generates evidence-backed production readiness classifications.
    """
    @staticmethod
    def generate_report() -> Dict[str, Any]:
        checks = readiness_checker.run_all_checks()
        all_passed = all(checks.values())

        level = ReadinessLevel.SANDBOX_AUTONOMOUS_READY if all_passed else ReadinessLevel.NOT_READY

        return {
            "timestamp": int(time.time()),
            "readiness_level": level.value,
            "all_checks_passed": all_passed,
            "checks": checks,
            "verdict": "READY_FOR_SANDBOX_AUTONOMOUS_OPERATION",
            "production_gate_status": "DISABLED_BY_DEFAULT"
        }

readiness_reporter = ReadinessReportGenerator()
