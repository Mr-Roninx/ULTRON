from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CivilizationGoldenScenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    customer_tier: str
    amount: float
    failure_code: str
    rail: str
    primary_gateway: str
    expected_optimal_action: str
    scheduled_chaos: List[Dict[str, Any]] = Field(default_factory=list)

CIVILIZATION_GOLDEN_SCENARIOS: List[CivilizationGoldenScenario] = [
    CivilizationGoldenScenario(scenario_id="01_TRANSIENT_SWITCH", name="Transient Switch ISO 91", description="Issuer rebooting for 10 mins", customer_tier="B2B_ENTERPRISE", amount=42000.0, failure_code="91", rail="CARD", primary_gateway="GATEWAY_A", expected_optimal_action="WAIT"),
    CivilizationGoldenScenario(scenario_id="02_INSUFFICIENT_FUNDS_SALARY", name="Payday Lag ISO 51", description="Customer salary inflow at T+24h", customer_tier="SMB", amount=18500.0, failure_code="51", rail="CARD", primary_gateway="GATEWAY_A", expected_optimal_action="SEND_PAYMENT_LINK"),
    CivilizationGoldenScenario(scenario_id="03_EXPIRED_MANDATE", name="Expired Subscription Mandate", description="ISO 14 recurring card mandate expired", customer_tier="MID_MARKET", amount=9500.0, failure_code="14", rail="UPI", primary_gateway="GATEWAY_B", expected_optimal_action="SEND_PAYMENT_LINK"),
    CivilizationGoldenScenario(scenario_id="04_ANANYA_TEXTILES_CHAOS", name="Ananya Textiles Gateway Degradation", description="Gateway A crash at T+2h requiring dynamic replan", customer_tier="B2B_ENTERPRISE", amount=24700.0, failure_code="91", rail="CARD", primary_gateway="GATEWAY_A", expected_optimal_action="WAIT", scheduled_chaos=[{"time_offset": 7200, "type": "GATEWAY_DEGRADATION", "target": "GATEWAY_A", "degraded_health": 0.08}]),
    CivilizationGoldenScenario(scenario_id="05_OVERDUE_ENTERPRISE_INVOICE", name="Strategic Enterprise Net-60 Overdue", description="Disputed PO item on ₹180k invoice", customer_tier="B2B_ENTERPRISE", amount=180000.0, failure_code="51", rail="BANK_TRANSFER", primary_gateway="GATEWAY_C", expected_optimal_action="ESCALATE")
]

def get_civilization_scenario(scenario_id: str) -> Optional[CivilizationGoldenScenario]:
    for s in CIVILIZATION_GOLDEN_SCENARIOS:
        if s.scenario_id == scenario_id or s.scenario_id.startswith(scenario_id):
            return s
    return None
