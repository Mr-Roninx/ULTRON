from typing import Dict, Any, List
from simulator.world import world

class CustomerRevenueGraph:
    def get_customer_exposure(self, customer_id: str) -> Dict[str, Any]:
        """
        Computes multi-opportunity interference graph.
        Returns aggregate exposure and related opportunities.
        """
        # Node types: CUSTOMER, PAYMENT, CHECKOUT, INVOICE, COMMUNICATION, PTP, GATEWAY
        
        related_payments = [p for p in world.payments.values() if p.customer_id == customer_id]
        related_invoices = [i for i in world.invoices.values() if i.customer_id == customer_id]
        related_checkouts = [c for c in world.checkouts.values() if c.customer_id == customer_id]
        
        # Calculate exposure
        failed_payments = sum(p.amount for p in related_payments if p.status.value == "FAILED")
        overdue_invoices = sum(i.amount for i in related_invoices if i.status.value == "OVERDUE")
        abandoned_checkouts = sum(c.amount for c in related_checkouts if c.status.value == "ABANDONED")
        
        total_exposure = failed_payments + overdue_invoices + abandoned_checkouts
        active_opportunities = len([p for p in related_payments if p.status.value == "FAILED"]) + \
                               len([i for i in related_invoices if i.status.value == "OVERDUE"]) + \
                               len([c for c in related_checkouts if c.status.value == "ABANDONED"])
                               
        customer = world.customers.get(customer_id)
        if customer:
            from backend.economics.relationship import RelationshipState
            rel_state = RelationshipState(
                customer_id=customer.id,
                recent_contacts=customer.recent_contacts,
                recent_responses=customer.recent_responses,
                successful_prior_recoveries=customer.successful_prior_recoveries,
                customer_value=customer.ltv,
                complaints=customer.complaints,
                opt_out=False,
                silence_duration=customer.silence_duration
            )
        else:
            rel_state = None
        
        # Cross channel risk increases exponentially with the number of active issues
        # If there are >1 active issues, interference is high.
        cross_channel_risk = 0.0
        if active_opportunities > 1:
            cross_channel_risk = (active_opportunities - 1) * 0.25
            
        interference_score = min(1.0, cross_channel_risk)
        
        return {
            "customer_id": customer_id,
            "total_exposure": total_exposure,
            "active_opportunities": active_opportunities,
            "interference_score": interference_score,
            "cross_channel_risk": cross_channel_risk,
            "relationship_cost": rel_state.relationship_cost_proxy() if rel_state else 0.0
        }

interference_engine = CustomerRevenueGraph()
