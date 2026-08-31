from typing import Dict, Any
from simulator.models import Customer, Payment, PaymentStatus, Invoice, InvoiceStatus, Checkout, CheckoutStatus, Gateway
from simulator.world import world
from simulator.clock import clock
from backend.payment_intelligence.rail_health import rail_health_engine

def setup_scenario_transient_failure(customer_id: str = "c_scen_transient") -> Dict[str, Any]:
    """Scenario 1: Transient issuer timeout (code 91). Gateway B is healthy (0.94)."""
    world.add_customer(Customer(id=customer_id, name="Apex Logistics", segment="B2B_ENTERPRISE", created_at=0))
    world.add_payment(Payment(
        id=f"p_{customer_id}",
        customer_id=customer_id,
        amount=6500.0,
        status=PaymentStatus.FAILED,
        failure_code="91",
        rail="CARD",
        gateway_id="GATEWAY_B",
        created_at=clock.now()
    ))
    rail_health_engine.restore_gateway("GATEWAY_B", target_health=0.94)
    return {"scenario_id": "SCEN_1_TRANSIENT", "customer_id": customer_id, "payment_id": f"p_{customer_id}", "amount": 6500.0}

def setup_scenario_liquidity_failure(customer_id: str = "c_scen_liquidity") -> Dict[str, Any]:
    """Scenario 2: Insufficient funds (code 51). Customer action required."""
    world.add_customer(Customer(id=customer_id, name="Bright Studio", segment="SMB", created_at=0))
    world.add_payment(Payment(
        id=f"p_{customer_id}",
        customer_id=customer_id,
        amount=3200.0,
        status=PaymentStatus.FAILED,
        failure_code="51",
        rail="UPI",
        gateway_id="GATEWAY_A",
        created_at=clock.now()
    ))
    return {"scenario_id": "SCEN_2_LIQUIDITY", "customer_id": customer_id, "payment_id": f"p_{customer_id}", "amount": 3200.0}

def setup_scenario_credential_failure(customer_id: str = "c_scen_credential") -> Dict[str, Any]:
    """Scenario 3: Card expired or stolen (code 14). Hard decline on card rail."""
    world.add_customer(Customer(id=customer_id, name="Crown Media", segment="B2B_MIDMARKET", created_at=0))
    world.add_payment(Payment(
        id=f"p_{customer_id}",
        customer_id=customer_id,
        amount=14000.0,
        status=PaymentStatus.FAILED,
        failure_code="14",
        rail="CARD",
        gateway_id="GATEWAY_B",
        created_at=clock.now()
    ))
    return {"scenario_id": "SCEN_3_CREDENTIAL", "customer_id": customer_id, "payment_id": f"p_{customer_id}", "amount": 14000.0}

def setup_scenario_gateway_degradation(customer_id: str = "c_scen_gw_degraded") -> Dict[str, Any]:
    """Scenario 4: Gateway B health degraded to 20%. Alternate Gateway A/C healthy."""
    world.add_customer(Customer(id=customer_id, name="Delta Tech", segment="B2B_ENTERPRISE", created_at=0))
    world.add_payment(Payment(
        id=f"p_{customer_id}",
        customer_id=customer_id,
        amount=9500.0,
        status=PaymentStatus.FAILED,
        failure_code="91",
        rail="CARD",
        gateway_id="GATEWAY_B",
        created_at=clock.now()
    ))
    rail_health_engine.degrade_gateway("GATEWAY_B", target_health=0.20)
    rail_health_engine.restore_gateway("GATEWAY_A", target_health=0.96)
    return {"scenario_id": "SCEN_4_GATEWAY_DEGRADATION", "customer_id": customer_id, "payment_id": f"p_{customer_id}", "amount": 9500.0}

def setup_scenario_ambiguous_state(customer_id: str = "c_scen_ambiguous") -> Dict[str, Any]:
    """Scenario 5: Timeout during authorization, payment in UNKNOWN state."""
    world.add_customer(Customer(id=customer_id, name="Echo Global", segment="B2B_ENTERPRISE", created_at=0))
    world.add_payment(Payment(
        id=f"p_{customer_id}",
        customer_id=customer_id,
        amount=8000.0,
        status=PaymentStatus.UNKNOWN,
        failure_code="GATEWAY_TIMEOUT",
        rail="ACH",
        gateway_id="GATEWAY_C",
        created_at=clock.now()
    ))
    return {"scenario_id": "SCEN_5_AMBIGUOUS_STATE", "customer_id": customer_id, "payment_id": f"p_{customer_id}", "amount": 8000.0}

def setup_scenario_mixed_exposure(customer_id: str = "c_scen_mixed") -> Dict[str, Any]:
    """Scenario 6: Multi-opportunity exposure (Subscription + Invoice + Abandoned Checkout)."""
    world.add_customer(Customer(id=customer_id, name="Ananya Textiles", segment="B2B_ENTERPRISE", created_at=0))
    world.add_payment(Payment(
        id=f"p_sub_{customer_id}",
        customer_id=customer_id,
        amount=8200.0,
        status=PaymentStatus.FAILED,
        failure_code="91",
        rail="CARD",
        gateway_id="GATEWAY_B",
        created_at=clock.now()
    ))
    world.add_invoice(Invoice(
        id=f"inv_{customer_id}",
        customer_id=customer_id,
        amount=4500.0,
        status=InvoiceStatus.OVERDUE,
        due_date=clock.now() - 86400,
        created_at=clock.now() - (86400 * 15)
    ))
    world.add_checkout(Checkout(
        id=f"chk_{customer_id}",
        customer_id=customer_id,
        amount=12000.0,
        status=CheckoutStatus.ABANDONED,
        created_at=clock.now() - 3600
    ))
    return {"scenario_id": "SCEN_6_MIXED_EXPOSURE", "customer_id": customer_id, "total_exposure": 24700.0}

SCENARIO_SETUP_MAP = {
    "SCEN_1_TRANSIENT": setup_scenario_transient_failure,
    "SCEN_2_LIQUIDITY": setup_scenario_liquidity_failure,
    "SCEN_3_CREDENTIAL": setup_scenario_credential_failure,
    "SCEN_4_GATEWAY_DEGRADATION": setup_scenario_gateway_degradation,
    "SCEN_5_AMBIGUOUS_STATE": setup_scenario_ambiguous_state,
    "SCEN_6_MIXED_EXPOSURE": setup_scenario_mixed_exposure
}
