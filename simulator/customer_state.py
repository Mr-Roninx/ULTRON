import simulator.world
from typing import Dict, Any
from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus
from backend.economics.relationship import RelationshipState

class CustomerStateEngine:
    def get_snapshot(self, customer_id: str) -> Dict[str, Any]:
        curr_world = simulator.world.world
        if customer_id not in curr_world.customers:
            raise ValueError("Customer not found")
            
        customer = curr_world.customers[customer_id]
        
        payments = [p.model_dump() for p in curr_world.payments.values() if p.customer_id == customer_id]
        failed_payments = [p for p in payments if str(p.get("status", "")).endswith("FAILED") or p.get("status") == PaymentStatus.FAILED or p.get("status") == PaymentStatus.FAILED.value]
        
        invoices = [i.model_dump() for i in curr_world.invoices.values() if i.customer_id == customer_id]
        overdue_invoices = [i for i in invoices if str(i.get("status", "")).endswith("OVERDUE") or i.get("status") == InvoiceStatus.OVERDUE or i.get("status") == InvoiceStatus.OVERDUE.value]
        
        checkouts = [c.model_dump() for c in curr_world.checkouts.values() if c.customer_id == customer_id]
        abandoned_checkouts = [c for c in checkouts if str(c.get("status", "")).endswith("ABANDONED") or c.get("status") == CheckoutStatus.ABANDONED or c.get("status") == CheckoutStatus.ABANDONED.value]
        
        exposure = sum(p["amount"] for p in failed_payments) + \
                   sum(i["amount"] for i in overdue_invoices) + \
                   sum(c["amount"] for c in abandoned_checkouts)
                   
        rel_state = RelationshipState(
            customer_id=customer.id,
            recent_contacts=customer.recent_contacts,
            recent_responses=customer.recent_responses,
            successful_prior_recoveries=customer.successful_prior_recoveries,
            customer_value=customer.ltv,
            complaints=customer.complaints,
            opt_out=customer.opt_out,
            silence_duration=customer.silence_duration
        )
                   
        return {
            "customer": customer.model_dump(),
            "payments": payments,
            "failed_payments": failed_payments,
            "invoices": invoices,
            "overdue_invoices": overdue_invoices,
            "checkouts": checkouts,
            "abandoned_checkouts": abandoned_checkouts,
            "total_exposure": exposure,
            "relationship_state": rel_state
        }

customer_state_engine = CustomerStateEngine()
