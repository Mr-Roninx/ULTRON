import random
from typing import List, Dict, Any, Tuple, Optional
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import (
    Customer, Merchant, Payment, PaymentAttempt, Checkout, Subscription,
    Invoice, InvoiceLineItem, Dispute, GroundTruthOutcome
)
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.schema.taxonomy import FailureTaxonomy, NormalizedFailureCode
from synthetic_payment_universe.schema.visibility import EventVisibility
from synthetic_payment_universe.generator.seeds import MasterSeedManager

FAILURE_CODE_WEIGHTS = {
    "91": 0.35, # Transient system/issuer outage
    "51": 0.25, # Insufficient funds
    "14": 0.15, # Expired/invalid credential
    "TO": 0.10, # Gateway timeout
    "61": 0.05, # Daily withdrawal limit
    "65": 0.04, # Velocity limit
    "54": 0.03, # Expired card
    "41": 0.01, # Lost card / hard decline
    "96": 0.01, # System malfunction
    "AMBIGUOUS_SETTLEMENT": 0.01 # Webhook delay / clearing pending
}

class PaymentUniverseGenerator:
    """
    Generates realistic synthetic payments, longitudinal customer histories,
    multi-state outcome distributions, and latent ground truth root causes.
    """
    def __init__(self, seed_manager: MasterSeedManager):
        self.seed_mgr = seed_manager

    def generate_payment_scenario(
        self,
        payment_index: int,
        customer: Customer,
        merchant: Merchant,
        created_at_override: Optional[int] = None
    ) -> Tuple[Payment, List[PaymentAttempt], GroundTruthOutcome]:
        subseed = self.seed_mgr.get_payment_seed(payment_index)
        rng = random.Random(subseed)

        created_at = created_at_override or clock.now()
        amt = round(rng.uniform(customer.average_transaction_value * 0.7, customer.average_transaction_value * 1.3), 2)
        rail = rng.choice(["CARD", "UPI", "ACH", "BANK_TRANSFER"])
        gw_id = merchant.primary_gateway_id if rng.random() > 0.3 else merchant.secondary_gateway_id

        pid = f"pmt_synth_{payment_index:07d}"

        # Determine outcome probabilistically based on customer success rate
        roll = rng.random()
        succ_thresh = customer.historical_success_rate # e.g. ~0.85

        if roll < succ_thresh:
            # 1. Successful payment (~85%)
            status = "SETTLED"
            pmt = Payment(
                payment_id=pid,
                customer_id=customer.customer_id,
                merchant_id=merchant.merchant_id,
                amount=amt,
                status=status,
                rail=rail,
                gateway_id=gw_id,
                failure_code=None,
                attempt_count=1,
                created_at=created_at,
                metadata={"merchant_industry": merchant.industry}
            )
            attempt = PaymentAttempt(
                attempt_id=f"att_{pid}_1",
                payment_id=pid,
                attempt_number=1,
                rail=rail,
                gateway_id=gw_id,
                status="SUCCESS",
                latency_ms=round(rng.uniform(80.0, 250.0), 1),
                timestamp=created_at
            )
            truth = GroundTruthOutcome(
                truth_id=f"gt_{pid}",
                payment_id=pid,
                true_root_cause="NONE_SUCCESS",
                eventual_payment=True,
                eventual_recovery_amount=amt,
                oracle_optimal_action="NO_ACTION_REQUIRED"
            )
            return pmt, [attempt], truth

        elif roll < succ_thresh + 0.02:
            # 2. Asynchronous Pending Settlement (~2%)
            status = "PENDING"
            pmt = Payment(
                payment_id=pid,
                customer_id=customer.customer_id,
                merchant_id=merchant.merchant_id,
                amount=amt,
                status=status,
                rail=rail,
                gateway_id=gw_id,
                failure_code="AMBIGUOUS_SETTLEMENT",
                attempt_count=1,
                created_at=created_at,
                metadata={"merchant_industry": merchant.industry}
            )
            attempt = PaymentAttempt(
                attempt_id=f"att_{pid}_1",
                payment_id=pid,
                attempt_number=1,
                rail=rail,
                gateway_id=gw_id,
                status="PENDING",
                failure_code="AMBIGUOUS_SETTLEMENT",
                latency_ms=round(rng.uniform(1500.0, 5000.0), 1),
                timestamp=created_at
            )
            truth = GroundTruthOutcome(
                truth_id=f"gt_{pid}",
                payment_id=pid,
                true_root_cause="ASYNCHRONOUS_CLEARING_LAG",
                eventual_payment=True,
                eventual_recovery_amount=amt,
                natural_recovery_timestamp=created_at + 7200,
                oracle_optimal_action="RECONCILE"
            )
            return pmt, [attempt], truth

        elif roll < succ_thresh + 0.03:
            # 3. Disputed Payment (~1%)
            status = "DISPUTED"
            pmt = Payment(
                payment_id=pid,
                customer_id=customer.customer_id,
                merchant_id=merchant.merchant_id,
                amount=amt,
                status=status,
                rail=rail,
                gateway_id=gw_id,
                failure_code="CHARGEBACK_DISPUTE",
                attempt_count=1,
                created_at=created_at,
                metadata={"merchant_industry": merchant.industry}
            )
            attempt = PaymentAttempt(
                attempt_id=f"att_{pid}_1",
                payment_id=pid,
                attempt_number=1,
                rail=rail,
                gateway_id=gw_id,
                status="FAILED",
                failure_code="CHARGEBACK_DISPUTE",
                latency_ms=150.0,
                timestamp=created_at
            )
            truth = GroundTruthOutcome(
                truth_id=f"gt_{pid}",
                payment_id=pid,
                true_root_cause="UNAUTHORIZED_TRANSACTION_CLAIM",
                eventual_payment=False,
                eventual_recovery_amount=0.0,
                oracle_optimal_action="ESCALATE"
            )
            return pmt, [attempt], truth

        else:
            # 4. Failed Payment (~12%)
            codes = list(FAILURE_CODE_WEIGHTS.keys())
            weights = list(FAILURE_CODE_WEIGHTS.values())
            fcode = rng.choices(codes, weights=weights, k=1)[0]
            code_info = FailureTaxonomy.get_code_info(fcode)
            true_root = rng.choice(code_info.possible_true_root_causes)

            status = "FAILED"
            natural_rec = (fcode in ["91", "TO"] and rng.random() > 0.40)
            natural_rec_time = created_at + rng.randint(3600, 28800) if natural_rec else None

            # Oracle optimal action
            if fcode == "91":
                opt_act = "WAIT" if natural_rec else "RETRY_GATEWAY_B"
            elif fcode == "51":
                opt_act = "SEND_PAYMENT_LINK"
            elif fcode == "14":
                opt_act = "SEND_PAYMENT_LINK"
            elif fcode == "41":
                opt_act = "ESCALATE"
            else:
                opt_act = "RETRY"

            pmt = Payment(
                payment_id=pid,
                customer_id=customer.customer_id,
                merchant_id=merchant.merchant_id,
                amount=amt,
                status=status,
                rail=rail,
                gateway_id=gw_id,
                failure_code=fcode,
                failure_reason=code_info.description,
                attempt_count=1,
                created_at=created_at,
                metadata={"merchant_industry": merchant.industry}
            )

            attempt = PaymentAttempt(
                attempt_id=f"att_{pid}_1",
                payment_id=pid,
                attempt_number=1,
                rail=rail,
                gateway_id=gw_id,
                status="FAILED",
                failure_code=fcode,
                latency_ms=round(rng.uniform(120.0, 3500.0), 1),
                timestamp=created_at
            )

            truth = GroundTruthOutcome(
                truth_id=f"gt_{pid}",
                payment_id=pid,
                true_root_cause=true_root,
                eventual_payment=natural_rec,
                eventual_recovery_amount=amt if natural_rec else 0.0,
                natural_recovery_timestamp=natural_rec_time,
                oracle_optimal_action=opt_act
            )

            return pmt, [attempt], truth

    def generate_customer_longitudinal_history(
        self,
        customer: Customer,
        merchant: Merchant,
        event_count: int = 5,
        base_index: int = 0
    ) -> List[Tuple[Payment, List[PaymentAttempt], GroundTruthOutcome]]:
        """
        Generates a realistic chronological sequence of historical payments
        preceding the current simulation clock.
        """
        history: List[Tuple[Payment, List[PaymentAttempt], GroundTruthOutcome]] = []
        now = clock.now()
        step_seconds = (customer.tenure_days * 86400) // max(1, event_count)

        for i in range(event_count):
            t = (now - (customer.tenure_days * 86400)) + (i * step_seconds)
            p_idx = base_index + i
            pmt, atts, truth = self.generate_payment_scenario(
                payment_index=p_idx,
                customer=customer,
                merchant=merchant,
                created_at_override=t
            )
            history.append((pmt, atts, truth))

        return history

    def generate_b2b_invoice_with_dispute(
        self,
        invoice_index: int,
        buyer: Customer,
        seller: Merchant
    ) -> Tuple[Invoice, Optional[Dispute]]:
        subseed = self.seed_mgr.get_payment_seed(invoice_index + 500000)
        rng = random.Random(subseed)

        inv_id = f"inv_synth_{invoice_index:06d}"
        amt = round(rng.uniform(50000.0, 500000.0), 2)
        has_dispute = (rng.random() < 0.15) # 15% dispute rate on enterprise invoices

        dispute = None
        if has_dispute:
            dtype = rng.choice(["MISSING_PO", "WRONG_PO", "LINE_ITEM_MISMATCH", "TAX_MISMATCH", "CONTRACT_MISMATCH"])
            req_human = dtype in ["LINE_ITEM_MISMATCH", "CONTRACT_MISMATCH"]
            dispute = Dispute(
                dispute_id=f"disp_{inv_id}",
                invoice_id=inv_id,
                dispute_type=dtype,
                status="OPEN",
                requires_human_intervention=req_human
            )

        inv = Invoice(
            invoice_id=inv_id,
            buyer_id=buyer.customer_id,
            seller_id=seller.merchant_id,
            amount=amt,
            due_timestamp=clock.now() + (30 * 86400),
            status="DISPUTED" if has_dispute else "OPEN",
            po_number=f"PO_{rng.randint(10000, 99999)}" if not (has_dispute and dispute.dispute_type == "MISSING_PO") else None,
            dispute_id=dispute.dispute_id if dispute else None
        )

        return inv, dispute
