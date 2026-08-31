from typing import Dict, List, Optional
from synthetic_payment_universe.schema.scenarios import GoldenScenarioDefinition

GOLDEN_SCENARIOS: List[GoldenScenarioDefinition] = [
    GoldenScenarioDefinition(
        scenario_id="01_TRANSIENT_ISSUER_TIMEOUT",
        name="Transient Issuer Timeout (ISO 91)",
        description="Major private bank switch reboot causing temporary 91 errors for 15 minutes.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=38500.0,
        iso_failure_code="91",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.96,
        future_events=[{"time_offset": 900, "event_type": "ISSUER_SWITCH_RESTORED"}],
        evaluation_target="WAIT_OR_RETRY"
    ),
    GoldenScenarioDefinition(
        scenario_id="02_INSUFFICIENT_FUNDS",
        name="Insufficient Funds / Payday Lag (ISO 51)",
        description="Enterprise client with temporary cashflow dip 2 days before monthly settlement cycle.",
        customer_segment="MID_MARKET",
        initial_amount=18400.0,
        iso_failure_code="51",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[{"time_offset": 86400, "event_type": "SALARY_INFLOW_RECEIVED"}],
        evaluation_target="SEND_PAYMENT_LINK"
    ),
    GoldenScenarioDefinition(
        scenario_id="03_EXPIRED_CARD",
        name="Expired Corporate Card Credential (ISO 14)",
        description="Expired corporate credit card credential with alternate authorized UPI rail available.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=45000.0,
        iso_failure_code="14",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="SWITCH_PERMITTED_RAIL_OR_LINK"
    ),
    GoldenScenarioDefinition(
        scenario_id="04_ANANYA_TEXTILES_GATEWAY_CHAOS",
        name="Ananya Textiles Mid-Flight Gateway Chaos",
        description="Ananya Textiles invoice recovery (INR 24,700, ISO 91) encountering Gateway A degradation at T+2h.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=24700.0,
        iso_failure_code="91",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[
            {
                "time_offset": 7200,
                "event_type": "GATEWAY_DEGRADATION",
                "gateway_id": "GATEWAY_A",
                "degraded_health": 0.10
            }
        ],
        evaluation_target="CHAOS_REPLAN_TO_LEARN"
    ),
    GoldenScenarioDefinition(
        scenario_id="05_GATEWAY_OUTAGE",
        name="Catastrophic Primary Gateway Outage",
        description="Complete outage on Gateway A requiring dynamic rerouting to Gateway B.",
        customer_segment="SMB",
        initial_amount=12500.0,
        iso_failure_code="TO",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.05,
        future_events=[],
        evaluation_target="SWITCH_GATEWAY_B"
    ),
    GoldenScenarioDefinition(
        scenario_id="06_UPI_FAILURE",
        name="UPI PSP Server Timeout (ISO 96)",
        description="Intermittent UPI handle failure on primary virtual payment address.",
        customer_segment="B2C",
        initial_amount=2200.0,
        iso_failure_code="96",
        initial_rail="UPI",
        initial_gateway="GATEWAY_B",
        initial_gateway_health=0.88,
        future_events=[],
        evaluation_target="RETRY_UPI"
    ),
    GoldenScenarioDefinition(
        scenario_id="07_UPI_FALLBACK",
        name="UPI Autopay Mandate Revoked",
        description="Revoked recurring UPI mandate requiring dynamic payment link checkout.",
        customer_segment="SMB",
        initial_amount=8900.0,
        iso_failure_code="14",
        initial_rail="UPI",
        initial_gateway="GATEWAY_B",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="SEND_PAYMENT_LINK"
    ),
    GoldenScenarioDefinition(
        scenario_id="08_CLEARING_TIMEOUT",
        name="Asynchronous Clearing Timeout (AMBIGUOUS)",
        description="Bank response timed out during high-volume clearing window.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=95000.0,
        iso_failure_code="AMBIGUOUS_SETTLEMENT",
        initial_rail="BANK_TRANSFER",
        initial_gateway="GATEWAY_C",
        initial_gateway_health=0.92,
        future_events=[],
        evaluation_target="RECONCILE"
    ),
    GoldenScenarioDefinition(
        scenario_id="09_UNKNOWN_PAYMENT_STATE",
        name="Dropped Webhook Settlement State",
        description="Payment debited from customer but webhook dropped in flight.",
        customer_segment="MID_MARKET",
        initial_amount=34000.0,
        iso_failure_code="AMBIGUOUS_SETTLEMENT",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.90,
        future_events=[],
        evaluation_target="RECONCILE"
    ),
    GoldenScenarioDefinition(
        scenario_id="10_DUPLICATE_WEBHOOK",
        name="Duplicate Webhook Delivery Storm",
        description="Gateway sends 3 identical success webhooks within 5 seconds.",
        customer_segment="SMB",
        initial_amount=5400.0,
        iso_failure_code="91",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="IDEMPOTENCY_DEDUPLICATION"
    ),
    GoldenScenarioDefinition(
        scenario_id="11_CHECKOUT_ABANDONMENT",
        name="High-Value Checkout OTP Abandonment",
        description="Customer abandons cart at 3DS step due to SMS delivery delay.",
        customer_segment="B2C",
        initial_amount=15600.0,
        iso_failure_code="3DS_FAILED",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="SEND_PAYMENT_LINK"
    ),
    GoldenScenarioDefinition(
        scenario_id="12_B2B_PO_DISPUTE",
        name="Enterprise Invoice PO Number Mismatch",
        description="Enterprise buyer accounts payable rejects invoice due to line item discrepancy.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=140000.0,
        iso_failure_code="51",
        initial_rail="BANK_TRANSFER",
        initial_gateway="GATEWAY_C",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="ESCALATE"
    ),
    GoldenScenarioDefinition(
        scenario_id="13_CUSTOMER_FATIGUE",
        name="Customer Fatigue / Excessive Outreach",
        description="Customer with 4 previous complaints and high contact fatigue.",
        customer_segment="MID_MARKET",
        initial_amount=28000.0,
        iso_failure_code="51",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="WAIT_OR_DISCOUNT"
    ),
    GoldenScenarioDefinition(
        scenario_id="14_MULTI_OPPORTUNITY",
        name="Cross-Opportunity Multi-Invoice Overlap",
        description="Client with active subscription failure and 2 overdue project invoices.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=85000.0,
        iso_failure_code="91",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="INTERFERENCE_AWARE_ACTION"
    ),
    GoldenScenarioDefinition(
        scenario_id="15_LIQUIDITY_WINDOW",
        name="Predictable Month-End Inflow Window",
        description="SMB account with established cashflow inflow on the 1st of the month.",
        customer_segment="SMB",
        initial_amount=19500.0,
        iso_failure_code="51",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[{"time_offset": 172800, "event_type": "MONTH_END_SETTLEMENT"}],
        evaluation_target="SCHEDULED_RETRY"
    ),
    GoldenScenarioDefinition(
        scenario_id="16_HARD_DECLINE",
        name="Fraud Block / Stolen Card (ISO 41)",
        description="Hard decline due to stolen card report requiring immediate stop and escalation.",
        customer_segment="B2C",
        initial_amount=7500.0,
        iso_failure_code="41",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="STOP_OR_ESCALATE"
    ),
    GoldenScenarioDefinition(
        scenario_id="17_ALTERNATE_RAIL",
        name="Card Limit Exceeded with Net Banking Active",
        description="Daily card limit exceeded (ISO 61) but Corporate Net Banking available.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=62000.0,
        iso_failure_code="61",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.95,
        future_events=[],
        evaluation_target="SWITCH_PERMITTED_RAIL"
    ),
    GoldenScenarioDefinition(
        scenario_id="18_CHAOS_REPLAN",
        name="Multi-Wave Environmental Chaos",
        description="Gateway degradation followed by webhook latency spike.",
        customer_segment="MID_MARKET",
        initial_amount=31000.0,
        iso_failure_code="TO",
        initial_rail="CARD",
        initial_gateway="GATEWAY_A",
        initial_gateway_health=0.90,
        future_events=[
            {"time_offset": 3600, "event_type": "GATEWAY_DEGRADATION", "degraded_health": 0.20},
            {"time_offset": 7200, "event_type": "WEBHOOK_DELAY", "delay_seconds": 3600}
        ],
        evaluation_target="MULTI_REPLAN_RESILIENCE"
    ),
    GoldenScenarioDefinition(
        scenario_id="19_HIGH_VALUE_ENTERPRISE",
        name="Tier-1 Global Enterprise Strategic Account",
        description="High LTV enterprise client ($1M+ annual spend) requiring zero aggressive touch.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=480000.0,
        iso_failure_code="51",
        initial_rail="BANK_TRANSFER",
        initial_gateway="GATEWAY_C",
        initial_gateway_health=0.98,
        future_events=[],
        evaluation_target="RELATIONSHIP_PRESERVATION"
    ),
    GoldenScenarioDefinition(
        scenario_id="20_AMBIGUOUS_SETTLEMENT",
        name="Cross-Border Multi-Currency Clearing Delay",
        description="Cross-border wire transfer in clearing hold between correspondent banks.",
        customer_segment="B2B_ENTERPRISE",
        initial_amount=210000.0,
        iso_failure_code="AMBIGUOUS_SETTLEMENT",
        initial_rail="BANK_TRANSFER",
        initial_gateway="GATEWAY_D",
        initial_gateway_health=0.92,
        future_events=[],
        evaluation_target="RECONCILE"
    )
]

def get_golden_scenario(scenario_id: str) -> Optional[GoldenScenarioDefinition]:
    for s in GOLDEN_SCENARIOS:
        if s.scenario_id == scenario_id or s.scenario_id.startswith(scenario_id):
            return s
    return None
