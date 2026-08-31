import os
import json
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from simulator.clock import clock
from backend.audit.trace import scrub_trace_payload

TRACES_DIR = "d:/Work Space/Project/Ultron/results/phase16/traces"
os.makedirs(TRACES_DIR, exist_ok=True)

class TraceNode(BaseModel):
    step_index: int
    event_type: str
    phase: str
    simulation_time: int
    wall_clock_time: float
    actor: str
    llm_invocation_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None
    preferred_action: Optional[str] = None
    candidate_actions: List[str] = Field(default_factory=list)
    deterministic_action: Optional[str] = None
    authority_override: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)

class CausalTraceGraph(BaseModel):
    run_id: str
    mission_id: str
    customer_id: str
    created_at: int
    completed_at: Optional[int] = None
    total_llm_invocations: int = 0
    replan_count: int = 0
    chaos_detected: bool = False
    final_status: str = "IN_PROGRESS"
    nodes: List[TraceNode] = Field(default_factory=list)

class TraceGraphEngine:
    """
    Constructs and persists causal execution trace graphs for ULTRON agent runs.
    Enables judges and evaluators to inspect exact multi-invocation causal chains.
    """
    def __init__(self):
        self._active_traces: Dict[str, CausalTraceGraph] = {}

    def start_trace(self, mission_id: str, customer_id: str, run_id: Optional[str] = None) -> str:
        rid = run_id or f"run_{uuid.uuid4().hex[:8]}"
        trace = CausalTraceGraph(
            run_id=rid,
            mission_id=mission_id,
            customer_id=customer_id,
            created_at=clock.now()
        )
        self._active_traces[mission_id] = trace
        return rid

    def add_node(
        self,
        mission_id: str,
        event_type: str,
        phase: str,
        actor: str = "AGENT_LOOP",
        llm_invocation_id: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        latency_ms: Optional[float] = None,
        preferred_action: Optional[str] = None,
        candidate_actions: Optional[List[str]] = None,
        deterministic_action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[TraceNode]:
        trace = self._active_traces.get(mission_id)
        if not trace:
            self.start_trace(mission_id, "customer_unknown")
            trace = self._active_traces.get(mission_id)

        step_idx = len(trace.nodes) + 1
        is_override = bool(preferred_action and deterministic_action and (preferred_action != deterministic_action))
        
        scrubbed_details = scrub_trace_payload(details or {})

        node = TraceNode(
            step_index=step_idx,
            event_type=event_type,
            phase=phase,
            simulation_time=clock.now(),
            wall_clock_time=clock.now(),
            actor=actor,
            llm_invocation_id=llm_invocation_id,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            preferred_action=preferred_action,
            candidate_actions=candidate_actions or [],
            deterministic_action=deterministic_action,
            authority_override=is_override,
            details=scrubbed_details
        )
        trace.nodes.append(node)

        if llm_invocation_id:
            trace.total_llm_invocations += 1
        if event_type == "REPLAN":
            trace.replan_count += 1
        if "CHAOS" in event_type or "DEGRADATION" in event_type:
            trace.chaos_detected = True

        return node

    def export_trace(self, mission_id: str, filepath: Optional[str] = None) -> Optional[str]:
        trace = self._active_traces.get(mission_id)
        if not trace:
            return None

        trace.completed_at = clock.now()
        trace.final_status = "COMPLETED"
        out_path = filepath or os.path.join(TRACES_DIR, f"{trace.run_id}.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(trace.model_dump_json(indent=2))

        return out_path

    def get_trace(self, mission_id: str) -> Optional[CausalTraceGraph]:
        return self._active_traces.get(mission_id)

    def reset(self):
        self._active_traces.clear()

trace_graph_engine = TraceGraphEngine()
