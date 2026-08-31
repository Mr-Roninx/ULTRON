import random
from typing import List, Dict, Any
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Merchant
from synthetic_payment_universe.generator.seeds import MasterSeedManager

MERCHANT_INDUSTRIES = [
    "SaaS", "E-commerce", "Education", "Healthcare", "Manufacturing",
    "Logistics", "Professional Services", "Travel", "Hospitality",
    "B2B Services", "Retail", "Digital Services"
]

class MerchantGenerator:
    """
    Generates synthetic merchants with realistic multi-industry configurations,
    monthly transaction volumes, and gateway routing profiles.
    """
    def __init__(self, seed_manager: MasterSeedManager):
        self.seed_mgr = seed_manager

    def generate_merchant(self, index: int) -> Merchant:
        subseed = self.seed_mgr.get_merchant_seed(index)
        rng = random.Random(subseed)

        ind = rng.choice(MERCHANT_INDUSTRIES)
        vol = rng.uniform(500000.0, 50000000.0)

        if ind in ["SaaS", "Digital Services", "Education"]:
            sub_ratio = rng.uniform(0.60, 0.90)
            inv_ratio = 1.0 - sub_ratio
            aov = rng.uniform(1500.0, 30000.0)
        elif ind in ["Manufacturing", "Logistics", "B2B Services", "Professional Services"]:
            inv_ratio = rng.uniform(0.70, 0.95)
            sub_ratio = 1.0 - inv_ratio
            aov = rng.uniform(50000.0, 500000.0)
        else: # E-commerce, Retail, Travel, Hospitality
            sub_ratio = rng.uniform(0.05, 0.20)
            inv_ratio = 0.05
            aov = rng.uniform(500.0, 15000.0)

        return Merchant(
            merchant_id=f"m_synth_{index:05d}",
            name=f"Merchant {ind} {index}",
            industry=ind,
            country="IND",
            currency="INR",
            monthly_volume=round(vol, 2),
            average_order_value=round(aov, 2),
            subscription_ratio=round(sub_ratio, 3),
            invoice_ratio=round(inv_ratio, 3),
            refund_rate=round(rng.uniform(0.005, 0.030), 4),
            chargeback_rate=round(rng.uniform(0.0005, 0.0040), 4),
            primary_gateway_id="GATEWAY_A" if index % 2 == 0 else "GATEWAY_B",
            secondary_gateway_id="GATEWAY_C" if index % 2 == 0 else "GATEWAY_D",
            created_at=clock.now() - (365 * 86400)
        )

    def generate_batch(self, count: int, offset: int = 0) -> List[Merchant]:
        return [self.generate_merchant(offset + i) for i in range(count)]
