# ULTRON Synthetic Payment Universe v1.2 Data Model

## 1. Relational Entities
- **Customer**: `customer_id`, `tier`, `behavior_profile`, `fatigue_score`, `average_transaction_value`, `historical_success_rate`, `created_at`.
- **Merchant**: `merchant_id`, `industry`, `monthly_volume`, `primary_gateway_id`, `secondary_gateway_id`.
- **Payment**: `payment_id`, `customer_id`, `merchant_id`, `amount`, `currency`, `status`, `rail`, `gateway_id`, `failure_code`.
- **PaymentAttempt**: `attempt_id`, `payment_id`, `attempt_number`, `rail`, `gateway_id`, `status`, `latency_ms`.
- **LedgerEntry**: `entry_id`, `transaction_id`, `account_debit`, `account_credit`, `amount`, `currency`, `timestamp`.
- **GroundTruth**: `truth_id`, `payment_id`, `true_root_cause`, `eventual_payment`, `natural_recovery_timestamp`, `oracle_optimal_action`.
