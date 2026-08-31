from typing import Dict, Any, Optional
from simulator.clock import clock

class SimulatedCustomerActor:
    """
    Simulates realistic B2B/SMB customer responsiveness, fatigue, liquidity cycles,
    and payment link conversions in a sandbox environment.
    """
    def __init__(self, customer_id: str, segment: str = "B2B_ENTERPRISE", liquidity_delay_hours: int = 24):
        self.customer_id = customer_id
        self.segment = segment
        self.liquidity_delay_hours = liquidity_delay_hours
        self.contact_count = 0
        self.opted_out = False

    def receive_contact(self, channel: str) -> Dict[str, Any]:
        self.contact_count += 1
        if self.contact_count >= 5:
            self.opted_out = True
        return {
            "customer_id": self.customer_id,
            "channel": channel,
            "total_contacts": self.contact_count,
            "opted_out": self.opted_out,
            "timestamp": clock.now()
        }

    def respond_to_payment_link(self, conversion_prob: float = 0.65) -> bool:
        if self.opted_out:
            return False
        return (conversion_prob >= 0.50)
