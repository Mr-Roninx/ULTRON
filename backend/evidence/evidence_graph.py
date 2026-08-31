import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class EvidenceNode(BaseModel):
    stage: str
    event_id: str
    timestamp: int
    source_type: str
    evidence_class: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EvidenceGraph(BaseModel):
    correlation_id: str
    nodes: List[EvidenceNode] = Field(default_factory=list)

    def add_node(
        self,
        stage: str,
        event_id: str,
        source_type: str,
        evidence_class: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.nodes.append(EvidenceNode(
            stage=stage,
            event_id=event_id,
            timestamp=int(time.time()),
            source_type=source_type,
            evidence_class=evidence_class,
            metadata=metadata or {}
        ))

    def get_provenance_summary(self) -> Dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "total_nodes": len(self.nodes),
            "stages": [n.stage for n in self.nodes],
            "evidence_classes_present": list(set(n.evidence_class for n in self.nodes)),
            "all_connected": len(self.nodes) >= 6
        }
