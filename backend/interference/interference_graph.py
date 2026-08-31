from typing import Dict, Any, List
from simulator.world import world

class InterferenceGraph:
    """
    Constructs multi-opportunity graph for a customer across failed payments,
    overdue invoices, abandoned checkouts, and prior communications.
    """
    def get_customer_exposure(self, customer_id: str) -> Dict[str, Any]:
        related_payments = [p for p in world.payments.values() if p.customer_id == customer_id]
        related_invoices = [i for i in world.invoices.values() if i.customer_id == customer_id]
        related_checkouts = [c for c in world.checkouts.values() if c.customer_id == customer_id]
        
        # Calculate exposure
        failed_payments = sum(p.amount for p in related_payments if getattr(p.status, "value", p.status) in ["FAILED", "UNKNOWN", "RECONCILING"])
        overdue_invoices = sum(i.amount for i in related_invoices if getattr(i.status, "value", i.status) in ["OVERDUE", "OPEN", "FAILED"])
        abandoned_checkouts = sum(c.amount for c in related_checkouts if getattr(c.status, "value", c.status) in ["ABANDONED", "PENDING"])
        
        total_exposure = failed_payments + overdue_invoices + abandoned_checkouts
        active_opportunities = len([p for p in related_payments if getattr(p.status, "value", p.status) in ["FAILED", "UNKNOWN"]]) + \
                               len([i for i in related_invoices if getattr(i.status, "value", i.status) in ["OVERDUE", "OPEN"]]) + \
                               len([c for c in related_checkouts if getattr(c.status, "value", c.status) in ["ABANDONED"]])
                               
        customer = world.customers.get(customer_id)
        
        cross_channel_risk = 0.0
        if active_opportunities > 1:
            cross_channel_risk = min(1.0, (active_opportunities - 1) * 0.25)
            
        interference_score = cross_channel_risk
        
        return {
            "customer_id": customer_id,
            "total_exposure": round(total_exposure, 2),
            "active_opportunities": active_opportunities,
            "interference_score": round(interference_score, 4),
            "cross_channel_risk": round(cross_channel_risk, 4),
            "failed_payments_amount": round(failed_payments, 2),
            "overdue_invoices_amount": round(overdue_invoices, 2),
            "abandoned_checkouts_amount": round(abandoned_checkouts, 2)
        }

interference_graph = InterferenceGraph()
