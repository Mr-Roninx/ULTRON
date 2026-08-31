from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class FailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    CUSTOMER_ACTION_REQUIRED = "CUSTOMER_ACTION_REQUIRED"
    HARD_DECLINE = "HARD_DECLINE"
    CONFIGURATION = "CONFIGURATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    AMBIGUOUS = "AMBIGUOUS"
    SETTLEMENT = "SETTLEMENT"
    RECONCILIATION = "RECONCILIATION"
    FRAUD_RISK = "FRAUD_RISK"
    LIMIT = "LIMIT"
    AUTHENTICATION = "AUTHENTICATION"
    TIMEOUT = "TIMEOUT"
    WEBHOOK_LATENCY = "WEBHOOK_LATENCY"
    OUT_OF_ORDER = "OUT_OF_ORDER"

class NormalizedFailureCode(BaseModel):
    observed_code: str
    category: FailureCategory
    description: str
    recoverable_by_retry: bool
    recoverable_by_customer_action: bool
    requires_human_escalation: bool
    possible_true_root_causes: List[str] = Field(default_factory=list)

class FailureTaxonomy:
    """Authoritative normalized failure taxonomy for payment universe simulation."""
    CATALOG: Dict[str, NormalizedFailureCode] = {
        "91": NormalizedFailureCode(
            observed_code="91",
            category=FailureCategory.TRANSIENT,
            description="System Error / Issuer or Switch Inoperative",
            recoverable_by_retry=True,
            recoverable_by_customer_action=False,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "ISSUER_CORE_BANKING_REBOOT",
                "SWITCH_NETWORK_INTERRUPTION",
                "GATEWAY_INTERNAL_TIMEOUT",
                "RAIL_TRANSIENT_SPIKE"
            ]
        ),
        "51": NormalizedFailureCode(
            observed_code="51",
            category=FailureCategory.CUSTOMER_ACTION_REQUIRED,
            description="Insufficient Funds / Balance Depleted",
            recoverable_by_retry=True, # Recoverable after salary/cashflow cycle
            recoverable_by_customer_action=True,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "PAYDAY_TIMING_LAG",
                "TEMPORARY_PREAUTH_HOLD",
                "ACCOUNT_DRAINED",
                "OVERDRAFT_LIMIT_EXCEEDED"
            ]
        ),
        "14": NormalizedFailureCode(
            observed_code="14",
            category=FailureCategory.CUSTOMER_ACTION_REQUIRED,
            description="Invalid Card Number / Expired Credential",
            recoverable_by_retry=False,
            recoverable_by_customer_action=True,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "CARD_EXPIRED",
                "TOKEN_REVOKED",
                "TYPO_IN_CARD_NUMBER"
            ]
        ),
        "41": NormalizedFailureCode(
            observed_code="41",
            category=FailureCategory.HARD_DECLINE,
            description="Lost Card / Pick Up",
            recoverable_by_retry=False,
            recoverable_by_customer_action=False,
            requires_human_escalation=True,
            possible_true_root_causes=[
                "CARD_REPORTED_LOST",
                "FRAUDULENT_CARD_BLOCK"
            ]
        ),
        "54": NormalizedFailureCode(
            observed_code="54",
            category=FailureCategory.HARD_DECLINE,
            description="Expired Card",
            recoverable_by_retry=False,
            recoverable_by_customer_action=True,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "CARD_VALIDITY_EXPIRED"
            ]
        ),
        "61": NormalizedFailureCode(
            observed_code="61",
            category=FailureCategory.LIMIT,
            description="Exceeds Withdrawal Amount Limit",
            recoverable_by_retry=True,
            recoverable_by_customer_action=True,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "DAILY_PER_TXN_LIMIT",
                "MONTHLY_UPI_LIMIT_CROSSED"
            ]
        ),
        "65": NormalizedFailureCode(
            observed_code="65",
            category=FailureCategory.LIMIT,
            description="Exceeds Withdrawal Frequency Limit",
            recoverable_by_retry=True,
            recoverable_by_customer_action=False,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "TXN_FREQUENCY_VELOCITY_TRIGGERED"
            ]
        ),
        "96": NormalizedFailureCode(
            observed_code="96",
            category=FailureCategory.INFRASTRUCTURE,
            description="System Malfunction",
            recoverable_by_retry=True,
            recoverable_by_customer_action=False,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "GATEWAY_CLUSTER_CRASH",
                "ROUTING_TABLE_CORRUPTION"
            ]
        ),
        "TO": NormalizedFailureCode(
            observed_code="TO",
            category=FailureCategory.TIMEOUT,
            description="Gateway / Network Request Timeout",
            recoverable_by_retry=True,
            recoverable_by_customer_action=False,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "INGRESS_LATENCY_SPIKE",
                "GATEWAY_DEGRADATION"
            ]
        ),
        "AMBIGUOUS_SETTLEMENT": NormalizedFailureCode(
            observed_code="AMBIGUOUS_SETTLEMENT",
            category=FailureCategory.AMBIGUOUS,
            description="Clearing Pending / Webhook Dropped",
            recoverable_by_retry=False,
            recoverable_by_customer_action=False,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "WEBHOOK_DROPPED_IN_FLIGHT",
                "ASYNCHRONOUS_CLEARING_LAG"
            ]
        ),
        "3DS_FAILED": NormalizedFailureCode(
            observed_code="3DS_FAILED",
            category=FailureCategory.AUTHENTICATION,
            description="Customer 3DS Authentication Failure or Abandonment",
            recoverable_by_retry=False,
            recoverable_by_customer_action=True,
            requires_human_escalation=False,
            possible_true_root_causes=[
                "OTP_ENTERED_INCORRECTLY",
                "CHALLENGE_WINDOW_CLOSED"
            ]
        )
    }

    @classmethod
    def get_code_info(cls, code: str) -> NormalizedFailureCode:
        return cls.CATALOG.get(code, NormalizedFailureCode(
            observed_code=code,
            category=FailureCategory.AMBIGUOUS,
            description="Unknown Failure Code",
            recoverable_by_retry=False,
            recoverable_by_customer_action=False,
            requires_human_escalation=False,
            possible_true_root_causes=["UNKNOWN_ROOT_CAUSE"]
        ))
