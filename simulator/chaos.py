from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import random
import uuid
from simulator.world import world
from simulator.models import PaymentStatus, CheckoutStatus, Gateway
from simulator.clock import clock
from simulator.event_bus import event_bus
from simulator.events import DomainEvent
from backend.audit.ledger import audit_ledger
from backend.payment_intelligence.rail_health import rail_health_engine

class ChaosScenario(ABC):
    def __init__(self, name: str, severity: float = 1.0):
        if not (0.0 <= severity <= 1.0):
            raise ValueError(f"Severity must be between 0.0 and 1.0 (provided: {severity})")
        self.name = name
        self.severity = severity

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        pass

class GatewayDegradationScenario(ChaosScenario):
    def __init__(self, severity: float = 0.8):
        super().__init__("GATEWAY_DEGRADATION", severity)

    def execute(self, gateway_id: str = "GATEWAY_B", target_health: float = 0.20, **kwargs) -> Dict[str, Any]:
        gw_state = rail_health_engine.degrade_gateway(gateway_id, target_health=target_health)
        
        # Also update world.gateways if present
        if gateway_id in world.gateways:
            world.gateways[gateway_id].health = target_health
            world.gateways[gateway_id].failure_rate = round(1.0 - target_health, 2)

        now = clock.now()
        event = DomainEvent(
            event_id=f"E_CHAOS_{str(uuid.uuid4())[:6]}",
            event_type="CHAOS_GATEWAY_DEGRADED",
            entity_type="GATEWAY",
            entity_id=gateway_id,
            customer_id="SYSTEM",
            timestamp=now,
            new_state=gw_state.status.value,
            payload={"gateway_id": gateway_id, "new_health": target_health, "failure_rate": gw_state.failure_rate}
        )
        event_bus.publish(event)
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "gateway_id": gateway_id, "health": target_health}
        )
        return {"status": "INJECTED", "scenario": self.name, "gateway_id": gateway_id, "health": target_health}

class UpiDegradationScenario(ChaosScenario):
    def __init__(self, severity: float = 0.8):
        super().__init__("UPI_DEGRADATION", severity)

    def execute(self, gateway_id: str = "gw_razorpay", **kwargs) -> Dict[str, Any]:
        if gateway_id not in world.gateways:
            world.add_gateway(Gateway(id=gateway_id, name="Razorpay Primary", health=1.0, supported_rails=["UPI", "CARD"]))
            
        gw = world.gateways[gateway_id]
        gw.health = max(0.0, 1.0 - self.severity)
        gw.failure_rate = self.severity

        event = DomainEvent(
            event_id=f"E_CHAOS_{str(uuid.uuid4())[:6]}",
            event_type="CHAOS_UPI_DEGRADED",
            entity_type="GATEWAY",
            entity_id=gateway_id,
            customer_id="SYSTEM",
            timestamp=clock.now(),
            new_state="DEGRADED",
            payload={"gateway_id": gateway_id, "new_health": gw.health, "failure_rate": gw.failure_rate}
        )
        event_bus.publish(event)
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "gateway_id": gateway_id, "health": gw.health}
        )
        return {"status": "INJECTED", "scenario": self.name, "gateway_id": gateway_id, "health": gw.health}

class GatewayTimeoutScenario(ChaosScenario):
    def __init__(self, severity: float = 1.0):
        super().__init__("GATEWAY_TIMEOUT", severity)

    def execute(self, payment_id: str, **kwargs) -> Dict[str, Any]:
        if payment_id not in world.payments:
            raise ValueError(f"Payment {payment_id} not found in world.")
            
        payment = world.payments[payment_id]
        if payment.status in [PaymentStatus.INITIATED, PaymentStatus.AUTHORIZING]:
            world.update_payment_status(payment_id, PaymentStatus.UNKNOWN.value, failure_code="GATEWAY_TIMEOUT")
            
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "payment_id": payment_id, "status": "UNKNOWN"}
        )
        return {"status": "INJECTED", "scenario": self.name, "payment_id": payment_id, "new_status": "UNKNOWN"}

class WebhookDelayScenario(ChaosScenario):
    def __init__(self, severity: float = 0.5):
        super().__init__("WEBHOOK_DELAY", severity)

    def execute(self, payment_id: str, delay_seconds: int = 7200, **kwargs) -> Dict[str, Any]:
        if payment_id not in world.payments:
            raise ValueError(f"Payment {payment_id} not found in world.")
            
        def _deferred_webhook():
            if payment_id in world.payments and world.payments[payment_id].status == PaymentStatus.AUTHORIZING:
                world.update_payment_status(payment_id, PaymentStatus.AUTHORIZED.value)
                
        clock.schedule(clock.now() + delay_seconds, _deferred_webhook)
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "payment_id": payment_id, "delay_seconds": delay_seconds}
        )
        return {"status": "INJECTED", "scenario": self.name, "payment_id": payment_id, "delay_seconds": delay_seconds}

class GatewayRecoveryScenario(ChaosScenario):
    def __init__(self, severity: float = 0.0):
        super().__init__("GATEWAY_RECOVERY", severity)

    def execute(self, gateway_id: str = "GATEWAY_B", target_health: float = 1.0, **kwargs) -> Dict[str, Any]:
        gw_state = rail_health_engine.restore_gateway(gateway_id, target_health=target_health)
        
        if gateway_id in world.gateways:
            gw = world.gateways[gateway_id]
            gw.health = target_health
            gw.failure_rate = round(1.0 - target_health, 2)
            
        event_bus.publish(DomainEvent(
            event_id=f"E_CHAOS_{str(uuid.uuid4())[:6]}",
            event_type="CHAOS_GATEWAY_RECOVERED",
            entity_type="GATEWAY",
            entity_id=gateway_id,
            customer_id="SYSTEM",
            timestamp=clock.now(),
            new_state="HEALTHY",
            payload={"gateway_id": gateway_id, "health": target_health}
        ))
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "gateway_id": gateway_id, "health": target_health}
        )
        return {"status": "INJECTED", "scenario": self.name, "gateway_id": gateway_id, "health": target_health}

class MassCheckoutAbandonmentScenario(ChaosScenario):
    def __init__(self, severity: float = 1.0):
        super().__init__("MASS_CHECKOUT_ABANDONMENT", severity)

    def execute(self, customer_ids: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        abandoned_count = 0
        target_customers = set(customer_ids) if customer_ids else set(world.customers.keys())
        
        for chk_id, chk in list(world.checkouts.items()):
            if chk.customer_id in target_customers and chk.status == CheckoutStatus.STARTED:
                world.update_checkout_status(chk_id, CheckoutStatus.ABANDONED.value)
                abandoned_count += 1
                
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "abandoned_count": abandoned_count}
        )
        return {"status": "INJECTED", "scenario": self.name, "abandoned_count": abandoned_count}

class CustomerSilenceScenario(ChaosScenario):
    def __init__(self, severity: float = 1.0):
        super().__init__("CUSTOMER_SILENCE", severity)

    def execute(self, customer_id: str, silence_duration: int = 86400 * 14, **kwargs) -> Dict[str, Any]:
        if customer_id not in world.customers:
            raise ValueError(f"Customer {customer_id} not found.")
            
        cust = world.customers[customer_id]
        cust.silence_duration += silence_duration
        cust.recent_responses = 0
        
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "customer_id": customer_id, "silence_duration": cust.silence_duration}
        )
        return {"status": "INJECTED", "scenario": self.name, "customer_id": customer_id, "silence_duration": cust.silence_duration}

class PaymentStateAmbiguityScenario(ChaosScenario):
    def __init__(self, severity: float = 1.0):
        super().__init__("PAYMENT_STATE_AMBIGUITY", severity)

    def execute(self, payment_id: str, **kwargs) -> Dict[str, Any]:
        if payment_id not in world.payments:
            raise ValueError(f"Payment {payment_id} not found.")
            
        payment = world.payments[payment_id]
        if payment.status in [PaymentStatus.INITIATED, PaymentStatus.AUTHORIZING, PaymentStatus.CREATED]:
            world.update_payment_status(payment_id, PaymentStatus.UNKNOWN.value)
            
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "payment_id": payment_id, "new_state": "UNKNOWN"}
        )
        return {"status": "INJECTED", "scenario": self.name, "payment_id": payment_id, "new_state": "UNKNOWN"}

class MassPaymentFailureScenario(ChaosScenario):
    def __init__(self, severity: float = 0.8):
        super().__init__("MASS_PAYMENT_FAILURE", severity)

    def execute(self, gateway_id: str = "GATEWAY_A", **kwargs) -> Dict[str, Any]:
        failed_count = 0
        for p in world.payments.values():
            if getattr(p, "gateway_id", "").upper() == gateway_id.upper() and p.status in [PaymentStatus.CREATED, PaymentStatus.INITIATED]:
                world.update_payment_status(p.id, PaymentStatus.FAILED.value, failure_code="GATEWAY_DOWN")
                failed_count += 1

        rail_health_engine.degrade_gateway(gateway_id, target_health=0.10)
        
        event_bus.publish(DomainEvent(
            event_id=f"E_CHAOS_{str(uuid.uuid4())[:6]}",
            event_type="CHAOS_MASS_FAILURE",
            entity_type="GATEWAY",
            entity_id=gateway_id,
            customer_id="SYSTEM",
            timestamp=clock.now(),
            new_state="FAILED",
            payload={"gateway_id": gateway_id, "failed_count": failed_count}
        ))
        audit_ledger.log(
            event_type="CHAOS_INJECTED",
            actor="CHAOS_ENGINE",
            payload={"scenario": self.name, "gateway_id": gateway_id, "failed_count": failed_count}
        )
        return {"status": "INJECTED", "scenario": self.name, "gateway_id": gateway_id, "failed_count": failed_count}

class ChaosEngine:
    def __init__(self):
        self.enabled = False
        self.failure_probability = 0.0
        self.scenarios: Dict[str, ChaosScenario] = {
            "GATEWAY_DEGRADATION": GatewayDegradationScenario(),
            "UPI_DEGRADATION": UpiDegradationScenario(),
            "GATEWAY_TIMEOUT": GatewayTimeoutScenario(),
            "WEBHOOK_DELAY": WebhookDelayScenario(),
            "GATEWAY_RECOVERY": GatewayRecoveryScenario(),
            "MASS_CHECKOUT_ABANDONMENT": MassCheckoutAbandonmentScenario(),
            "CUSTOMER_SILENCE": CustomerSilenceScenario(),
            "PAYMENT_STATE_AMBIGUITY": PaymentStateAmbiguityScenario(),
            "MASS_PAYMENT_FAILURE": MassPaymentFailureScenario()
        }

    def enable(self, failure_probability: float = 0.5):
        self.enabled = True
        self.failure_probability = failure_probability

    def disable(self):
        self.enabled = False

    def trigger(self, scenario_name: str, **kwargs) -> Dict[str, Any]:
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown chaos scenario: {scenario_name}. Supported: {list(self.scenarios.keys())}")
        return self.scenarios[scenario_name].execute(**kwargs)

    def intercept_payment(self, payment_id: str) -> bool:
        if not self.enabled:
            return False
        if random.random() < self.failure_probability:
            if payment_id in world.payments:
                world.update_payment_status(payment_id, PaymentStatus.FAILED.value)
                return True
        return False

chaos_engine = ChaosEngine()
