from typing import Dict, Any
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus, Invoice, InvoiceStatus
from memory.episodic import memory_store
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.mission.mission_builder import mission_registry

class DemoScenarioRegistry:
    @staticmethod
    def setup_demo_01_transient_gateway() -> Dict[str, Any]:
        """DEMO_01: Transient Issuer Timeout (Apex Logistics, ₹6,500, ISO 91)."""
        world.reset()
        mission_registry.reset()
        clock.reset(1720000000)
        memory_store.clear()
        rail_health_engine.reset()

        cust = Customer(id="c_demo_01", name="Apex Logistics Pvt Ltd", segment="B2B_MIDMARKET", created_at=clock.now())
        world.add_customer(cust)

        pmt = Payment(
            id="pmt_demo_01",
            customer_id=cust.id,
            amount=6500.0,
            status=PaymentStatus.FAILED,
            rail="CARD",
            gateway_id="GATEWAY_B",
            created_at=clock.now(),
            failure_code="91",
            metadata={"failure_reason": "ISSUER_UNAVAILABLE"}
        )
        world.add_payment(pmt)
        return {"scenario_id": "DEMO_01_TRANSIENT_GATEWAY", "customer_id": cust.id, "payment_id": pmt.id, "amount": 6500.0}

    @staticmethod
    def setup_demo_02_insufficient_funds() -> Dict[str, Any]:
        """DEMO_02: Insufficient Funds (Bright Studio, ₹3,200, ISO 51)."""
        world.reset()
        mission_registry.reset()
        clock.reset(1720000000)
        memory_store.clear()
        rail_health_engine.reset()

        cust = Customer(id="c_demo_02", name="Bright Creative Studio", segment="SMB", created_at=clock.now())
        world.add_customer(cust)

        pmt = Payment(
            id="pmt_demo_02",
            customer_id=cust.id,
            amount=3200.0,
            status=PaymentStatus.FAILED,
            rail="UPI",
            gateway_id="GATEWAY_A",
            created_at=clock.now(),
            failure_code="51",
            metadata={"failure_reason": "INSUFFICIENT_FUNDS"}
        )
        world.add_payment(pmt)
        return {"scenario_id": "DEMO_02_INSUFFICIENT_FUNDS", "customer_id": cust.id, "payment_id": pmt.id, "amount": 3200.0}

    @staticmethod
    def setup_demo_03_expired_card() -> Dict[str, Any]:
        """DEMO_03: Hard Decline Expired Card (Crown Media, ₹14,000, ISO 14)."""
        world.reset()
        mission_registry.reset()
        clock.reset(1720000000)
        memory_store.clear()
        rail_health_engine.reset()

        cust = Customer(id="c_demo_03", name="Crown Media Enterprises", segment="B2B_MIDMARKET", created_at=clock.now())
        world.add_customer(cust)

        pmt = Payment(
            id="pmt_demo_03",
            customer_id=cust.id,
            amount=14000.0,
            status=PaymentStatus.FAILED,
            rail="CARD",
            gateway_id="GATEWAY_B",
            created_at=clock.now(),
            failure_code="14",
            metadata={"failure_reason": "INVALID_CARD_NUMBER"}
        )
        world.add_payment(pmt)
        return {"scenario_id": "DEMO_03_EXPIRED_CARD", "customer_id": cust.id, "payment_id": pmt.id, "amount": 14000.0}

    @staticmethod
    def setup_demo_04_gateway_chaos() -> Dict[str, Any]:
        """DEMO_04 (Primary Golden Demo): Ananya Textiles (₹24,700, ISO 91 + Mid-Flight Chaos)."""
        world.reset()
        mission_registry.reset()
        clock.reset(1720000000)
        memory_store.clear()
        rail_health_engine.reset()

        cust = Customer(id="c_ananya_enterprise", name="Ananya Textiles Pvt Ltd", segment="B2B_ENTERPRISE", created_at=clock.now())
        world.add_customer(cust)

        pmt = Payment(
            id="pmt_ananya_24700",
            customer_id=cust.id,
            amount=24700.0,
            status=PaymentStatus.FAILED,
            rail="CARD",
            gateway_id="GATEWAY_A",
            created_at=clock.now(),
            failure_code="91",
            metadata={"failure_reason": "ISSUER_UNAVAILABLE"}
        )
        world.add_payment(pmt)
        return {"scenario_id": "DEMO_04_GATEWAY_CHAOS", "customer_id": cust.id, "payment_id": pmt.id, "amount": 24700.0}

    @staticmethod
    def setup_demo_05_b2b_invoice() -> Dict[str, Any]:
        """DEMO_05: Overdue Enterprise Net-30 Invoice (Zenith Heavy Industries, ₹185,000)."""
        world.reset()
        mission_registry.reset()
        clock.reset(1720000000)
        memory_store.clear()
        rail_health_engine.reset()

        cust = Customer(id="c_demo_05", name="Zenith Heavy Industries Ltd", segment="B2B_ENTERPRISE", created_at=clock.now())
        world.add_customer(cust)

        inv = Invoice(
            id="inv_zenith_185000",
            customer_id=cust.id,
            amount=185000.0,
            status=InvoiceStatus.OVERDUE,
            due_date=clock.now() - (15 * 86400)
        )
        world.add_invoice(inv)

        pmt = Payment(
            id="pmt_demo_05",
            customer_id=cust.id,
            amount=185000.0,
            status=PaymentStatus.FAILED,
            rail="BANK_TRANSFER",
            gateway_id="GATEWAY_C",
            created_at=clock.now(),
            failure_code="TO",
            metadata={"failure_reason": "CLEARING_TIMEOUT"}
        )
        world.add_payment(pmt)
        return {"scenario_id": "DEMO_05_B2B_INVOICE", "customer_id": cust.id, "payment_id": pmt.id, "amount": 185000.0}

DEMO_SCENARIO_MAP = {
    "DEMO_01_TRANSIENT_GATEWAY": DemoScenarioRegistry.setup_demo_01_transient_gateway,
    "DEMO_02_INSUFFICIENT_FUNDS": DemoScenarioRegistry.setup_demo_02_insufficient_funds,
    "DEMO_03_EXPIRED_CARD": DemoScenarioRegistry.setup_demo_03_expired_card,
    "DEMO_04_GATEWAY_CHAOS": DemoScenarioRegistry.setup_demo_04_gateway_chaos,
    "DEMO_05_B2B_INVOICE": DemoScenarioRegistry.setup_demo_05_b2b_invoice,
}
