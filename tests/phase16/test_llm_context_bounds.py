import pytest
from backend.llm.context_builder import context_builder
from simulator.clock import clock

def test_context_builder_bounds_and_strips_bloat():
    clock.reset(1700000000)
    raw_context = {
        "customer": {"id": "c_test_corp", "segment": "B2B_ENTERPRISE"},
        "payment": {"id": "pmt_1", "amount": 25000.0, "rail": "CARD", "gateway_id": "GATEWAY_A", "failure_code": "91"},
        "diagnosis": {"primary_reason": "ISSUER_UNAVAILABLE", "failure_class": "INFRASTRUCTURE", "recoverability": 0.65},
        "redundant_huge_logs": ["log_" + str(i) for i in range(5000)] # Bloat
    }

    messages = context_builder.build_optimized_prompt(raw_context, ["WAIT", "RETRY_GATEWAY_A"])
    prompt_str = str(messages)
    
    assert "redundant_huge_logs" not in prompt_str
    assert "ISSUER_UNAVAILABLE" in prompt_str
    assert "c_test_corp" in prompt_str
    assert len(prompt_str) < 3000
