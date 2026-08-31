from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class MechanismVerdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_SUPPORTED = "NOT_SUPPORTED"

class ExperimentIdentity(BaseModel):
    experiment_id: str
    run_id: str
    seed: int
    world_snapshot_hash: str
    configuration_hash: str
    agent_configuration: Dict[str, Any] = Field(default_factory=dict)
    mechanism_configuration: Dict[str, bool] = Field(default_factory=dict)
    timestamp: float

class LLMExecutionEvidence(BaseModel):
    experiment_id: str
    provider: str
    model: str
    latency_ms: float
    success: bool
    fallback_used: bool
    schema_valid: bool
    candidate_actions: List[str] = Field(default_factory=list)
    request_id: Optional[str] = None
    timestamp: float
    real_llm_execution: bool

class LLMCandidateInfluenceResult(BaseModel):
    scenario_id: str
    llm_candidates: List[str]
    deterministic_candidates: List[str]
    candidate_overlap: List[str]
    candidate_novelty_rate: float
    preferred_action: str
    final_authority_action: str
    nev: float
    outcome: str
    altered_decision: bool

class PaymentIntelligenceAblationResult(BaseModel):
    scenario_id: str
    failure_type: str
    full_ultron_diagnosis: str
    full_ultron_action: str
    no_pi_action: str
    decision_differed: bool
    full_ultron_recovery: float
    no_pi_recovery: float
    incremental_recovery: float
    full_ultron_nev: float
    no_pi_nev: float

class MemoryInfluenceResult(BaseModel):
    customer_id: str
    episode_1_action: str
    episode_1_error: float
    episode_2_memory_on_action: str
    episode_2_memory_off_action: str
    memory_retrieved: bool
    memory_influenced: bool
    memory_on_recovery: float
    memory_off_recovery: float
    memory_on_nev: float
    memory_off_nev: float

class ReplanningEvidenceResult(BaseModel):
    scenario_id: str
    original_action: str
    original_nev: float
    chaos_event: str
    gateway_health_before: float
    gateway_health_after: float
    plan_invalidated: bool
    replan_count: int
    new_action: str
    new_nev: float
    action_changed: bool

class EconomicLiftResult(BaseModel):
    seed: int
    total_at_risk: float
    no_action_recovery: float
    fixed_retry_recovery: float
    traditional_dunning_recovery: float
    rule_based_recovery: float
    ultron_recovery: float
    paired_incremental_vs_fixed_retry: float
    paired_incremental_vs_rule_based: float
    ultron_nev: float
    time_to_recovery: float

class StatisticalSummary(BaseModel):
    mean: float
    median: float
    std_dev: float
    ci_95_lower: float
    ci_95_upper: float
    sample_size: int
    effect_size: Optional[float] = None
    verdict: MechanismVerdict
    interpretation: str

class AblationMatrixRow(BaseModel):
    configuration: str
    seed: int
    gross_recovery: float
    incremental_recovery: float
    recovery_rate: float
    net_expected_value: float
    replan_count: int
    memory_influenced: bool
