from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus

class InvalidStateTransitionError(Exception):
    pass

class PaymentFSM:
    VALID_TRANSITIONS = {
        PaymentStatus.CREATED: {PaymentStatus.INITIATED, PaymentStatus.UNKNOWN, PaymentStatus.FAILED},
        PaymentStatus.INITIATED: {PaymentStatus.AUTHORIZING, PaymentStatus.FAILED, PaymentStatus.UNKNOWN},
        PaymentStatus.AUTHORIZING: {PaymentStatus.AUTHORIZED, PaymentStatus.FAILED, PaymentStatus.UNKNOWN},
        PaymentStatus.AUTHORIZED: {PaymentStatus.CAPTURED, PaymentStatus.FAILED, PaymentStatus.REVERSED, PaymentStatus.UNKNOWN},
        PaymentStatus.CAPTURED: {PaymentStatus.SETTLED, PaymentStatus.REFUNDED, PaymentStatus.REVERSED, PaymentStatus.UNKNOWN},
        PaymentStatus.SETTLED: {PaymentStatus.REVERSED, PaymentStatus.REFUNDED},
        PaymentStatus.FAILED: {PaymentStatus.INITIATED, PaymentStatus.UNKNOWN, PaymentStatus.SETTLED},
        PaymentStatus.UNKNOWN: {PaymentStatus.RECONCILING},
        PaymentStatus.RECONCILING: {PaymentStatus.AUTHORIZED, PaymentStatus.FAILED, PaymentStatus.SETTLED},
        PaymentStatus.REVERSED: set(),
        PaymentStatus.REFUNDED: set()
    }
    
    @classmethod
    def validate_transition(cls, current: PaymentStatus, target: PaymentStatus):
        if target not in cls.VALID_TRANSITIONS.get(current, set()):
            raise InvalidStateTransitionError(f"Cannot transition payment from {current} to {target}")

class InvoiceFSM:
    VALID_TRANSITIONS = {
        InvoiceStatus.CREATED: {InvoiceStatus.OVERDUE, InvoiceStatus.PAID},
        InvoiceStatus.OVERDUE: {InvoiceStatus.PAID},
        InvoiceStatus.PAID: set()
    }
    
    @classmethod
    def validate_transition(cls, current: InvoiceStatus, target: InvoiceStatus):
        if target not in cls.VALID_TRANSITIONS.get(current, set()):
            raise InvalidStateTransitionError(f"Cannot transition invoice from {current} to {target}")

class CheckoutFSM:
    VALID_TRANSITIONS = {
        CheckoutStatus.STARTED: {CheckoutStatus.ABANDONED, CheckoutStatus.COMPLETED},
        CheckoutStatus.ABANDONED: {CheckoutStatus.COMPLETED},
        CheckoutStatus.COMPLETED: set()
    }

    @classmethod
    def validate_transition(cls, current: CheckoutStatus, target: CheckoutStatus):
        if target not in cls.VALID_TRANSITIONS.get(current, set()):
            raise InvalidStateTransitionError(f"Cannot transition checkout from {current} to {target}")
