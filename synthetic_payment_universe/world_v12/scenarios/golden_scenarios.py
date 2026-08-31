from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GoldenWorldScenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    customer_segment: str
    amount: float
    failure_code: str
    rail: str
    gateway_id: str
    expected_optimal_action: str
    scheduled_chaos: List[Dict[str, Any]] = Field(default_factory=list)

GOLDEN_SCENARIOS_V12: List[GoldenWorldScenario] = [
    GoldenWorldScenario(scenario_id="01_TRANSIENT_ISSUER", name="Transient Issuer Switch Timeout", description="ISO 91 rebooting for 15 mins", customer_segment="B2B_ENTERPRISE", amount=38500.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="WAIT"),
    GoldenWorldScenario(scenario_id="02_INSUFFICIENT_FUNDS", name="Insufficient Funds (Payday Lag)", description="ISO 51 with salary arriving T+24h", customer_segment="MID_MARKET", amount=18400.0, failure_code="51", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="SEND_PAYMENT_LINK"),
    GoldenWorldScenario(scenario_id="03_EXPIRED_CARD", name="Expired Card Credential", description="ISO 14 corporate card expired", customer_segment="B2B_ENTERPRISE", amount=45000.0, failure_code="14", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="SEND_PAYMENT_LINK"),
    GoldenWorldScenario(scenario_id="04_GATEWAY_A_FAILURE", name="Catastrophic Gateway A Outage", description="Gateway A hardware switch crash", customer_segment="SMB", amount=12500.0, failure_code="TO", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="SWITCH_GATEWAY"),
    GoldenWorldScenario(scenario_id="05_GATEWAY_A_DEGRADATION", name="Gateway A Mid-Flight Chaos", description="Ananya Textiles degradation at T+2h", customer_segment="B2B_ENTERPRISE", amount=24700.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="WAIT", scheduled_chaos=[{"time_offset": 7200, "type": "GATEWAY_DEGRADATION", "target": "GATEWAY_A", "degraded_health": 0.10}]),
    GoldenWorldScenario(scenario_id="06_AMBIGUOUS_TIMEOUT", name="Ambiguous Clearing Timeout", description="Bank clearing hold requiring reconciliation", customer_segment="B2B_ENTERPRISE", amount=95000.0, failure_code="AMBIGUOUS_SETTLEMENT", rail="BANK_TRANSFER", gateway_id="GATEWAY_C", expected_optimal_action="RECONCILE"),
    GoldenWorldScenario(scenario_id="07_WEBHOOK_DELAY", name="Delayed Webhook Delivery", description="Settlement webhook delayed 1 hour", customer_segment="MID_MARKET", amount=34000.0, failure_code="AMBIGUOUS_SETTLEMENT", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="RECONCILE"),
    GoldenWorldScenario(scenario_id="08_WEBHOOK_DUPLICATION", name="Webhook Delivery Storm", description="Triplicate webhook delivery", customer_segment="SMB", amount=5400.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="WAIT"),
    GoldenWorldScenario(scenario_id="09_OUT_OF_ORDER_WEBHOOK", name="Out-of-Order Webhook Sequence", description="Success arriving before init", customer_segment="MID_MARKET", amount=14200.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="RECONCILE"),
    GoldenWorldScenario(scenario_id="10_ENTERPRISE_INVOICE", name="Enterprise PO Discrepancy", description="Accounts payable invoice mismatch", customer_segment="B2B_ENTERPRISE", amount=140000.0, failure_code="51", rail="BANK_TRANSFER", gateway_id="GATEWAY_C", expected_optimal_action="ESCALATE"),
    GoldenWorldScenario(scenario_id="11_SUBSCRIPTION_FAILURE", name="Recurring Subscription Failure", description="Expired mandate requiring checkout link", customer_segment="SMB", amount=8900.0, failure_code="14", rail="UPI", gateway_id="GATEWAY_B", expected_optimal_action="SEND_PAYMENT_LINK"),
    GoldenWorldScenario(scenario_id="12_MULTI_OPPORTUNITY", name="Cross-Opportunity Overlap", description="Subscription + 2 Overdue Invoices", customer_segment="B2B_ENTERPRISE", amount=85000.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="WAIT"),
    GoldenWorldScenario(scenario_id="13_CUSTOMER_FATIGUE", name="High Contact Fatigue", description="Customer fatigue > 0.85", customer_segment="MID_MARKET", amount=28000.0, failure_code="51", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="WAIT"),
    GoldenWorldScenario(scenario_id="14_NATURAL_RECOVERY", name="Natural Switch Recovery", description="Self-healing transient failure", customer_segment="SMB", amount=19500.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="WAIT"),
    GoldenWorldScenario(scenario_id="15_CHAOS_DURING_WAIT", name="Environmental Chaos During Wait", description="Outage occurs while agent is sleeping", customer_segment="MID_MARKET", amount=31000.0, failure_code="TO", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="SWITCH_GATEWAY", scheduled_chaos=[{"time_offset": 3600, "type": "GATEWAY_DEGRADATION", "target": "GATEWAY_A", "degraded_health": 0.05}]),
    GoldenWorldScenario(scenario_id="16_LLM_REPLAN", name="Multi-Step Adaptive Replan", description="Sequential intervention with feedback", customer_segment="B2B_ENTERPRISE", amount=62000.0, failure_code="91", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="RETRY"),
    GoldenWorldScenario(scenario_id="17_NEAR_TIED_NEV", name="Near-Tied 1-5% NEV Boundary", description="Ambiguous trade-off between Link and Retry", customer_segment="SMB", amount=15000.0, failure_code="51", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="SEND_PAYMENT_LINK"),
    GoldenWorldScenario(scenario_id="18_HIGH_VALUE_ENTERPRISE", name="Tier-1 Strategic Enterprise", description="LTV > 1M, zero aggressive touch", customer_segment="B2B_ENTERPRISE", amount=480000.0, failure_code="51", rail="BANK_TRANSFER", gateway_id="GATEWAY_C", expected_optimal_action="ESCALATE"),
    GoldenWorldScenario(scenario_id="19_LOW_VALUE_CUSTOMER", name="Micro-Payment Abandonment", description="Low amount where outreach cost > yield", customer_segment="B2C", amount=250.0, failure_code="51", rail="UPI", gateway_id="GATEWAY_B", expected_optimal_action="STOP"),
    GoldenWorldScenario(scenario_id="20_HARD_DECLINE", name="Fraud / Stolen Card (ISO 41)", description="Hard decline stop & human alert", customer_segment="B2C", amount=7500.0, failure_code="41", rail="CARD", gateway_id="GATEWAY_A", expected_optimal_action="ESCALATE")
]

def get_golden_scenario_v12(scenario_id: str) -> Optional[GoldenWorldScenario]:
    for s in GOLDEN_SCENARIOS_V12:
        if s.scenario_id == scenario_id or s.scenario_id.startswith(scenario_id):
            return s
    return None
