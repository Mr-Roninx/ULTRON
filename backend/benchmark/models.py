from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class SegmentType(str, Enum):
    B2B_ENTERPRISE = "B2B_ENTERPRISE"
    SMB = "SMB"
    RETAIL = "RETAIL"
    D2C = "D2C"

class OpportunityType(str, Enum):
    PAYMENT_FAILURE = "PAYMENT_FAILURE"
    OVERDUE_INVOICE = "OVERDUE_INVOICE"
    ABANDONED_CHECKOUT = "ABANDONED_CHECKOUT"

class AblationConfig(BaseModel):
    name: str = "FULL_ULTRON"
    disable_interference: bool = False
    disable_memory: bool = False
    disable_replanning: bool = False
    disable_decay: bool = False
    disable_relationship_cost: bool = False
    disable_payment_intelligence: bool = False

class ResourceConstraints(BaseModel):
    max_contacts_per_customer: int = 3
    max_recovery_actions_per_opportunity: int = 4
    max_human_hours: float = 100.0
    max_discount_percentage: float = 0.20
    max_risk_tolerance: float = 1.0
    authority_level: str = "AUTONOMOUS"

class BenchmarkOpportunity(BaseModel):
    opportunity_id: str
    customer_id: str
    customer_name: str
    customer_segment: str
    customer_ltv: float
    entity_type: str  # "PAYMENT", "INVOICE", "CHECKOUT"
    entity_id: str
    initial_amount: float
    failure_type: str
    payment_rail: str
    channel: str
    created_at: int
    days_overdue: int = 0
    amount_bucket: str = "MEDIUM"  # "MICRO", "LOW", "MEDIUM", "HIGH", "ENTERPRISE"

class OpportunityResult(BaseModel):
    opportunity_id: str
    customer_id: str
    initial_amount: float
    channel: str
    failure_type: str
    customer_segment: str
    payment_rail: str
    amount_bucket: str
    
    control_strategy: str
    control_action: Optional[str] = None
    control_recovered: float = 0.0
    control_contacts: int = 0
    control_cost: float = 0.0
    control_relationship_cost: float = 0.0
    
    treatment_strategy: str
    ultron_action: Optional[str] = None
    ultron_recovered: float = 0.0
    ultron_contacts: int = 0
    ultron_cost: float = 0.0
    ultron_relationship_cost: float = 0.0
    
    incremental_recovery: float = 0.0
    net_incremental_recovery: float = 0.0

class StrategyMetrics(BaseModel):
    strategy_name: str
    seed: int
    horizon_days: int
    revenue_at_risk: float = 0.0
    addressable_revenue: float = 0.0
    natural_recovery: float = 0.0
    gross_recovery: float = 0.0
    incremental_recovery: float = 0.0
    net_incremental_recovery: float = 0.0
    
    recovery_rate: float = 0.0  # gross_recovery / addressable_revenue
    incremental_recovery_rate: float = 0.0  # incremental_recovery / addressable_revenue
    
    actions_attempted: int = 0
    actions_successful: int = 0
    actions_blocked: int = 0
    escalations: int = 0
    customer_contacts: int = 0
    replans: int = 0
    avg_time_to_recovery_hours: float = 0.0
    
    intervention_cost: float = 0.0
    relationship_cost: float = 0.0
    risk_cost: float = 0.0
    total_cost: float = 0.0
    
    # Safety metrics
    policy_violations: int = 0
    fsm_violations: int = 0
    duplicate_actions: int = 0
    unauthorized_actions: int = 0
    future_information_leaks: int = 0
    
    # Efficiency metrics
    recovery_per_action: float = 0.0
    recovery_per_contact: float = 0.0
    recovery_per_operational_hour: float = 0.0

class AggregateMetrics(BaseModel):
    strategy_name: str
    sample_size_seeds: int
    horizon_days: int
    
    gross_recovery_mean: float
    gross_recovery_median: float
    gross_recovery_std: float
    gross_recovery_ci95: List[float]
    
    incremental_recovery_mean: float
    incremental_recovery_median: float
    incremental_recovery_std: float
    incremental_recovery_ci95: List[float]
    
    net_incremental_recovery_mean: float
    net_incremental_recovery_median: float
    net_incremental_recovery_std: float
    net_incremental_recovery_ci95: List[float]
    
    recovery_rate_mean: float
    recovery_rate_ci95: List[float]
    
    contacts_mean: float
    actions_mean: float
    replans_mean: float
    total_cost_mean: float
    
    policy_violations_total: int
    fsm_violations_total: int
    future_leaks_total: int

class SegmentMetrics(BaseModel):
    segment_dimension: str  # "customer_segment", "failure_type", "payment_rail", "amount_bucket"
    segment_value: str
    opportunity_count: int
    addressable_revenue: float
    control_recovered: float
    ultron_recovered: float
    incremental_recovery: float
    net_incremental_recovery: float
    ultron_win_rate: float
