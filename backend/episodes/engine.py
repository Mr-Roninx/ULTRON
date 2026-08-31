from pydantic import BaseModel
from typing import List
from simulator.clock import clock
from simulator.world import world

class RevenueEpisode(BaseModel):
    episode_id: str
    customer_id: str
    payments: List[str]        # payment IDs
    invoices: List[str]        # invoice IDs
    checkouts: List[str]       # checkout session IDs
    total_exposure: float
    created_at: int

class EpisodeEngine:
    def create_episode(self, customer_id: str) -> RevenueEpisode:
        # Aggregates all currently failing/open items for a customer
        from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus
        
        payment_ids = []
        invoice_ids = []
        checkout_ids = []
        exposure = 0.0
        
        # Find failed or unknown payments
        for pid, p in world.payments.items():
            if p.customer_id == customer_id and p.status in [PaymentStatus.FAILED, PaymentStatus.UNKNOWN]:
                payment_ids.append(pid)
                exposure += p.amount
                
        # Find overdue invoices
        for iid, inv in world.invoices.items():
            if inv.customer_id == customer_id and inv.status == InvoiceStatus.OVERDUE:
                invoice_ids.append(iid)
                exposure += inv.amount
                
        # Find abandoned checkouts
        for cid, chk in world.checkouts.items():
            if chk.customer_id == customer_id and chk.status == CheckoutStatus.ABANDONED:
                checkout_ids.append(cid)
                exposure += chk.amount
                
        episode = RevenueEpisode(
            episode_id=f"ep_{customer_id}_{clock.now()}",
            customer_id=customer_id,
            payments=payment_ids,
            invoices=invoice_ids,
            checkouts=checkout_ids,
            total_exposure=exposure,
            created_at=clock.now()
        )
        return episode
        
    def get_episodes(self, customer_id: str) -> List[RevenueEpisode]:
        # For now, it just generates the current episode state on the fly.
        # In a real system with persistence, this would query a database of historical episodes.
        return [self.create_episode(customer_id)]

episode_engine = EpisodeEngine()
