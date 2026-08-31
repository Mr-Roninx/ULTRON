import os
import time
from typing import Dict, List, Any, Optional
from simulator.clock import clock
from synthetic_payment_universe.generator.seeds import MasterSeedManager, PARTITION_SEED_RANGES
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator
from synthetic_payment_universe.generator.merchant_gen import MerchantGenerator
from synthetic_payment_universe.generator.gateway_gen import GatewayRailGenerator
from synthetic_payment_universe.generator.payment_gen import PaymentUniverseGenerator
from synthetic_payment_universe.generator.communication_gen import CommunicationGenerator
from synthetic_payment_universe.storage.jsonl_streamer import JSONLEventStreamer
from synthetic_payment_universe.storage.sqlite_engine import UniverseSQLiteEngine
from synthetic_payment_universe.storage.parquet_exporter import UniverseParquetExporter
from synthetic_payment_universe.schema.entities import (
    Customer, Merchant, Payment, PaymentAttempt, GroundTruthOutcome,
    Invoice, Dispute, Subscription, Checkout
)

DATASETS_BASE_DIR = "d:/Work Space/Project/Ultron/synthetic_payment_universe/datasets"

class SyntheticUniverseBuilder:
    """
    Master Builder for the ULTRON Synthetic Payment Universe v1.1.
    Enforces strict partition seed isolation, longitudinal history generation,
    and multi-opportunity cross-channel data modeling.
    """
    def __init__(self, master_seed: int = 12345):
        self.base_seed = master_seed

    def build_partition(
        self,
        partition_name: str,
        customer_count: int = 100,
        payments_per_customer: int = 10,
        out_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        start_t = time.time()
        seed_mgr = MasterSeedManager(master_seed=self.base_seed, partition_name=partition_name)
        partition_seed = seed_mgr.partition_seed
        target_dir = out_dir or os.path.join(DATASETS_BASE_DIR, partition_name)
        os.makedirs(target_dir, exist_ok=True)

        customer_gen = CustomerGenerator(seed_mgr)
        merchant_gen = MerchantGenerator(seed_mgr)
        payment_gen = PaymentUniverseGenerator(seed_mgr)

        customers = customer_gen.generate_batch(customer_count, offset=partition_seed * 100)
        merchant_count = max(5, customer_count // 10)
        merchants = merchant_gen.generate_batch(merchant_count, offset=partition_seed * 100)

        all_payments: List[Payment] = []
        all_attempts: List[PaymentAttempt] = []
        all_ground_truths: List[GroundTruthOutcome] = []
        all_invoices: List[Invoice] = []
        all_disputes: List[Dispute] = []

        pmt_idx = partition_seed * 1000
        inv_idx = partition_seed * 500

        for cust in customers:
            merch = merchants[pmt_idx % len(merchants)]

            # 1. Generate longitudinal historical transactions
            hist_count = max(0, payments_per_customer - 1)
            hist = payment_gen.generate_customer_longitudinal_history(
                customer=cust,
                merchant=merch,
                event_count=hist_count,
                base_index=pmt_idx
            )
            for p, atts, gt in hist:
                all_payments.append(p)
                all_attempts.extend(atts)
                all_ground_truths.append(gt)
                pmt_idx += 1

            # 2. Generate current/active payment scenario
            active_p, active_atts, active_gt = payment_gen.generate_payment_scenario(
                payment_index=pmt_idx,
                customer=cust,
                merchant=merch
            )
            all_payments.append(active_p)
            all_attempts.extend(active_atts)
            all_ground_truths.append(active_gt)
            pmt_idx += 1

            # 3. Multi-Opportunity Generation (B2B invoices with disputes)
            if cust.segment in ["B2B_ENTERPRISE", "MID_MARKET"]:
                inv, disp = payment_gen.generate_b2b_invoice_with_dispute(
                    invoice_index=inv_idx,
                    buyer=cust,
                    seller=merch
                )
                all_invoices.append(inv)
                if disp:
                    all_disputes.append(disp)
                inv_idx += 1

        # 1. Write Streaming JSONL
        JSONLEventStreamer.write_records(os.path.join(target_dir, "customers.jsonl"), customers)
        JSONLEventStreamer.write_records(os.path.join(target_dir, "merchants.jsonl"), merchants)
        JSONLEventStreamer.write_records(os.path.join(target_dir, "payments.jsonl"), all_payments)
        JSONLEventStreamer.write_records(os.path.join(target_dir, "payment_attempts.jsonl"), all_attempts)
        JSONLEventStreamer.write_records(os.path.join(target_dir, "ground_truth.jsonl"), all_ground_truths)
        JSONLEventStreamer.write_records(os.path.join(target_dir, "invoices.jsonl"), all_invoices)

        # 2. Write SQLite DB
        db_path = os.path.join(target_dir, "universe.db")
        sqlite_engine = UniverseSQLiteEngine(db_path)
        sqlite_engine.insert_batch(customers, merchants, all_payments, all_ground_truths)

        # 3. Export Parquet
        UniverseParquetExporter.export_records(os.path.join(target_dir, "customers.parquet"), customers)
        UniverseParquetExporter.export_records(os.path.join(target_dir, "payments.parquet"), all_payments)

        elapsed = time.time() - start_t

        return {
            "partition": partition_name,
            "partition_seed": partition_seed,
            "seed_range": PARTITION_SEED_RANGES.get(partition_name),
            "customers_generated": len(customers),
            "merchants_generated": len(merchants),
            "payments_generated": len(all_payments),
            "payment_attempts_generated": len(all_attempts),
            "ground_truths_generated": len(all_ground_truths),
            "invoices_generated": len(all_invoices),
            "disputes_generated": len(all_disputes),
            "duration_seconds": round(elapsed, 2),
            "target_dir": target_dir
        }
