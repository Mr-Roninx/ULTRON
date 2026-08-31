from simulator.models import Payment, PaymentStatus
from simulator.world import world
from financial.fsm import PaymentFSM

class ReconciliationEngine:
    def reconcile(self, payment_id: str, actual_status: PaymentStatus):
        payment = world.payments.get(payment_id)
        if not payment:
            return False
            
        if payment.status == PaymentStatus.UNKNOWN:
            # First transition to RECONCILING
            PaymentFSM.validate_transition(payment.status, PaymentStatus.RECONCILING)
            world.update_payment_status(payment_id, PaymentStatus.RECONCILING.value)
            
            # Then transition to actual status (SETTLED or FAILED)
            PaymentFSM.validate_transition(PaymentStatus.RECONCILING, actual_status)
            world.update_payment_status(payment_id, actual_status.value)
            return True
            
        return False

reconciliation = ReconciliationEngine()
