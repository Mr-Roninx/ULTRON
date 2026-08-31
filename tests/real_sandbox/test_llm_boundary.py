import pytest
from backend.agent.action_registry import action_registry

@pytest.mark.fixture
def test_llm_cannot_call_arbitrary_http_or_sql():
    ok_sql, _ = action_registry.validate_action("EXECUTE_RAW_SQL")
    ok_http, _ = action_registry.validate_action("ARBITRARY_HTTP_POST")
    assert ok_sql is False
    assert ok_http is False
