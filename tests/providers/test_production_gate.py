import pytest
from backend.readiness.checks import readiness_checker
from backend.readiness.report import readiness_reporter
from backend.readiness.levels import ReadinessLevel

def test_production_readiness_checks():
    checks = readiness_checker.run_all_checks()
    assert all(checks.values()) is True

    rep = readiness_reporter.generate_report()
    assert rep["readiness_level"] == ReadinessLevel.SANDBOX_AUTONOMOUS_READY.value
    assert rep["all_checks_passed"] is True
