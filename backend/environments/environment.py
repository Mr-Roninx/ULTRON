from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from backend.providers.models import CanonicalPayment, CanonicalPaymentState, CanonicalCustomer, CanonicalPaymentLink

class PaymentEnvironment(ABC):
    """
    Unified environment abstraction for ULTRON AgentLoop.
    Allows the same core agent loop to operate against either SWU or Real Providers.
    """
    def __init__(self, environment_name: str, is_synthetic: bool):
        self.environment_name = environment_name
        self.is_synthetic = is_synthetic

    @abstractmethod
    def observe_payment(self, payment_id: str) -> CanonicalPayment:
        pass

    @abstractmethod
    def observe_customer(self, customer_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute_action(
        self,
        action_type: str,
        customer_id: str,
        payment_id: str,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        pass

    @abstractmethod
    def reconcile(self, payment_id: str) -> Tuple[CanonicalPaymentState, str]:
        pass

    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        pass
