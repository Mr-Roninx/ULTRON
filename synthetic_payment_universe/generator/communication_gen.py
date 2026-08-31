import random
from typing import List, Dict, Any, Tuple
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Customer, Communication
from synthetic_payment_universe.generator.seeds import MasterSeedManager

CHANNELS = ["EMAIL", "SMS", "WHATSAPP", "VOICE", "IN_APP"]

class CommunicationGenerator:
    """
    Simulates customer outreach events, response latency, and contact fatigue.
    """
    def __init__(self, seed_manager: MasterSeedManager):
        self.seed_mgr = seed_manager

    def generate_communication(
        self,
        comm_index: int,
        customer: Customer,
        channel: str = "EMAIL",
        template: str = "PAYMENT_REMINDER"
    ) -> Tuple[Communication, bool]:
        subseed = self.seed_mgr.get_behavior_seed(comm_index)
        rng = random.Random(subseed)

        cid = f"comm_synth_{comm_index:06d}"
        now = clock.now()

        customer.contact_count += 1
        customer.fatigue_score = min(1.0, customer.fatigue_score + 0.15)
        if customer.fatigue_score >= 0.90:
            customer.is_opted_out = True

        # Determine response
        base_p = 0.60 - (customer.fatigue_score * 0.40)
        responded = (rng.random() < max(0.05, base_p)) and not customer.is_opted_out
        resp_time = now + rng.randint(300, 7200) if responded else None

        comm = Communication(
            communication_id=cid,
            customer_id=customer.customer_id,
            channel=channel,
            template=template,
            status="REPLIED" if responded else "DELIVERED",
            sent_timestamp=now,
            response_timestamp=resp_time
        )

        return comm, responded
