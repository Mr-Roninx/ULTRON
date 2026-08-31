from typing import Dict, Any, List, Optional
from backend.payment_intelligence.schemas import FailureClass, FailureSeverity

class TaxonomyRule:
    def __init__(
        self,
        failure_class: FailureClass,
        severity: FailureSeverity,
        base_recoverability: float,
        customer_action_required: bool,
        retry_eligible: bool,
        typical_recovery_actions: List[str],
        prohibited_actions: List[str],
        recommended_investigation: List[str]
    ):
        self.failure_class = failure_class
        self.severity = severity
        self.base_recoverability = base_recoverability
        self.customer_action_required = customer_action_required
        self.retry_eligible = retry_eligible
        self.typical_recovery_actions = typical_recovery_actions
        self.prohibited_actions = prohibited_actions
        self.recommended_investigation = recommended_investigation

DETERMINISTIC_TAXONOMY: Dict[str, TaxonomyRule] = {
    # 1. LIQUIDITY
    "INSUFFICIENT_FUNDS": TaxonomyRule(
        failure_class=FailureClass.LIQUIDITY,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.70,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["RETRY", "SEND_PAYMENT_LINK", "WAIT", "REGISTER_PTP"],
        prohibited_actions=["ESCALATE"],
        recommended_investigation=["historical_salary_day", "recent_payment_patterns", "account_balance_trend"]
    ),
    "LIMIT_EXCEEDED": TaxonomyRule(
        failure_class=FailureClass.LIQUIDITY,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.60,
        customer_action_required=True,
        retry_eligible=True,
        typical_recovery_actions=["REQUEST_CUSTOMER_ACTION", "SEND_PAYMENT_LINK", "SWITCH_PERMITTED_RAIL"],
        prohibited_actions=[],
        recommended_investigation=["transaction_amount", "card_tier", "alternative_payment_methods"]
    ),

    # 2. CREDENTIAL
    "EXPIRED_CARD": TaxonomyRule(
        failure_class=FailureClass.CREDENTIAL,
        severity=FailureSeverity.HIGH,
        base_recoverability=0.50,
        customer_action_required=True,
        retry_eligible=False,
        typical_recovery_actions=["SEND_PAYMENT_LINK", "REQUEST_CUSTOMER_ACTION", "SEND_MESSAGE"],
        prohibited_actions=["RETRY"],
        recommended_investigation=["stored_payment_methods", "last_successful_payment_date"]
    ),
    "INVALID_CVV": TaxonomyRule(
        failure_class=FailureClass.CREDENTIAL,
        severity=FailureSeverity.HIGH,
        base_recoverability=0.55,
        customer_action_required=True,
        retry_eligible=False,
        typical_recovery_actions=["REQUEST_CUSTOMER_ACTION", "SEND_PAYMENT_LINK"],
        prohibited_actions=["RETRY"],
        recommended_investigation=["customer_contact_channels", "recent_checkout_attempts"]
    ),
    "INVALID_CREDENTIALS": TaxonomyRule(
        failure_class=FailureClass.CREDENTIAL,
        severity=FailureSeverity.HIGH,
        base_recoverability=0.45,
        customer_action_required=True,
        retry_eligible=False,
        typical_recovery_actions=["REQUEST_CUSTOMER_ACTION", "SEND_PAYMENT_LINK"],
        prohibited_actions=["RETRY"],
        recommended_investigation=["payment_method_status", "auth_history"]
    ),

    # 3. ACCOUNT
    "CLOSED_ACCOUNT": TaxonomyRule(
        failure_class=FailureClass.ACCOUNT,
        severity=FailureSeverity.CRITICAL,
        base_recoverability=0.20,
        customer_action_required=True,
        retry_eligible=False,
        typical_recovery_actions=["REQUEST_CUSTOMER_ACTION", "ESCALATE"],
        prohibited_actions=["RETRY", "RECONCILE"],
        recommended_investigation=["relationship_state", "contract_status", "customer_profile"]
    ),
    "BLOCKED_ACCOUNT": TaxonomyRule(
        failure_class=FailureClass.ACCOUNT,
        severity=FailureSeverity.CRITICAL,
        base_recoverability=0.25,
        customer_action_required=True,
        retry_eligible=False,
        typical_recovery_actions=["REQUEST_CUSTOMER_ACTION", "ESCALATE"],
        prohibited_actions=["RETRY"],
        recommended_investigation=["compliance_flags", "fraud_score", "customer_tier"]
    ),
    "DO_NOT_HONOR": TaxonomyRule(
        failure_class=FailureClass.ACCOUNT,
        severity=FailureSeverity.HIGH,
        base_recoverability=0.35,
        customer_action_required=True,
        retry_eligible=False,
        typical_recovery_actions=["REQUEST_CUSTOMER_ACTION", "SEND_PAYMENT_LINK"],
        prohibited_actions=["RETRY"],
        recommended_investigation=["issuing_bank", "card_brand", "recent_chargebacks"]
    ),

    # 4. AUTHENTICATION
    "3D_SECURE_FAILED": TaxonomyRule(
        failure_class=FailureClass.AUTHENTICATION,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.75,
        customer_action_required=True,
        retry_eligible=True,
        typical_recovery_actions=["SEND_PAYMENT_LINK", "SEND_MESSAGE", "REQUEST_CUSTOMER_ACTION"],
        prohibited_actions=[],
        recommended_investigation=["device_fingerprint", "auth_channel", "browser_session"]
    ),
    "AUTH_REQUIRED": TaxonomyRule(
        failure_class=FailureClass.AUTHENTICATION,
        severity=FailureSeverity.LOW,
        base_recoverability=0.80,
        customer_action_required=True,
        retry_eligible=True,
        typical_recovery_actions=["SEND_PAYMENT_LINK", "SEND_MESSAGE"],
        prohibited_actions=[],
        recommended_investigation=["preferred_contact_method", "communication_fatigue"]
    ),
    "AUTH_TIMEOUT": TaxonomyRule(
        failure_class=FailureClass.AUTHENTICATION,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.70,
        customer_action_required=True,
        retry_eligible=True,
        typical_recovery_actions=["SEND_PAYMENT_LINK", "RETRY", "SEND_MESSAGE"],
        prohibited_actions=[],
        recommended_investigation=["network_latency", "otp_delivery_status"]
    ),

    # 5. INFRASTRUCTURE / NETWORK
    "TIMEOUT": TaxonomyRule(
        failure_class=FailureClass.INFRASTRUCTURE,
        severity=FailureSeverity.LOW,
        base_recoverability=0.85,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["RETRY", "WAIT", "RECONCILE"],
        prohibited_actions=["ESCALATE", "SEND_MESSAGE"],
        recommended_investigation=["gateway_health", "issuer_network_status", "transaction_latency"]
    ),
    "ISSUER_UNAVAILABLE": TaxonomyRule(
        failure_class=FailureClass.INFRASTRUCTURE,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.80,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["RETRY", "WAIT", "SWITCH_PERMITTED_RAIL"],
        prohibited_actions=["ESCALATE"],
        recommended_investigation=["bank_uptime_feed", "rail_health", "peak_hour_load"]
    ),
    "NETWORK_ERROR": TaxonomyRule(
        failure_class=FailureClass.INFRASTRUCTURE,
        severity=FailureSeverity.LOW,
        base_recoverability=0.85,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["RETRY", "WAIT"],
        prohibited_actions=["ESCALATE"],
        recommended_investigation=["connection_pool_health", "dns_latency"]
    ),

    # 6. GATEWAY
    "GATEWAY_DEGRADED": TaxonomyRule(
        failure_class=FailureClass.GATEWAY,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.80,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["RETRY", "SWITCH_PERMITTED_RAIL", "WAIT"],
        prohibited_actions=[],
        recommended_investigation=["active_gateway_instances", "failover_routes"]
    ),
    "GATEWAY_DOWN": TaxonomyRule(
        failure_class=FailureClass.GATEWAY,
        severity=FailureSeverity.HIGH,
        base_recoverability=0.70,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["SWITCH_PERMITTED_RAIL", "RETRY", "WAIT"],
        prohibited_actions=[],
        recommended_investigation=["gateway_health", "failover_availability", "webhook_status"]
    ),

    # 7. UNKNOWN
    "UNKNOWN_ERROR": TaxonomyRule(
        failure_class=FailureClass.UNKNOWN,
        severity=FailureSeverity.MEDIUM,
        base_recoverability=0.40,
        customer_action_required=False,
        retry_eligible=True,
        typical_recovery_actions=["RECONCILE", "RETRY", "ESCALATE"],
        prohibited_actions=[],
        recommended_investigation=["raw_error_payload", "gateway_logs", "recent_settlement_files"]
    )
}

class FailureTaxonomy:
    @staticmethod
    def get_rule(failure_reason: str) -> TaxonomyRule:
        return DETERMINISTIC_TAXONOMY.get(failure_reason, DETERMINISTIC_TAXONOMY["UNKNOWN_ERROR"])

    @staticmethod
    def is_retry_eligible(failure_reason: str) -> bool:
        return FailureTaxonomy.get_rule(failure_reason).retry_eligible

    @staticmethod
    def requires_customer_action(failure_reason: str) -> bool:
        return FailureTaxonomy.get_rule(failure_reason).customer_action_required

    @staticmethod
    def get_typical_actions(failure_reason: str) -> List[str]:
        return list(FailureTaxonomy.get_rule(failure_reason).typical_recovery_actions)

    @staticmethod
    def get_prohibited_actions(failure_reason: str) -> List[str]:
        return list(FailureTaxonomy.get_rule(failure_reason).prohibited_actions)

failure_taxonomy = FailureTaxonomy()
