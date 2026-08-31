import networkx as nx
from typing import Dict, Any, List, Optional
from simulator.event_bus import event_bus
from simulator.events import DomainEvent

class RevenueInterferenceEngine:
    """
    Computes Temporal Association and Cross-Event Interference between financial domain events.
    
    NOTE: In the absence of strict randomized control or instrumental variables,
    this metric quantifies empirical TEMPORAL ASSOCIATION: Delta = P(B | A) - P(B | NOT A).
    It does not claim unconfounded causal identification unless observational balance holds.
    """
    def __init__(self, temporal_window_seconds: int = 86400, min_sample_size: int = 1):
        self.graph = nx.DiGraph()
        self.temporal_window_seconds = temporal_window_seconds
        self.min_sample_size = min_sample_size

    def build_graph(self):
        self.graph.clear()
        events = event_bus.get_history()

        # Add events as typed nodes
        for e in events:
            self.graph.add_node(
                e.event_id,
                event_type=e.event_type,
                customer_id=e.customer_id,
                timestamp=e.timestamp,
                new_state=e.new_state
            )

        # Add temporal edges (events occurring within temporal window for the same customer)
        for i, e1 in enumerate(events):
            for j, e2 in enumerate(events[i+1:]):
                if e1.customer_id == e2.customer_id:
                    time_diff = e2.timestamp - e1.timestamp
                    if 0 <= time_diff <= self.temporal_window_seconds:
                        self.graph.add_edge(
                            e1.event_id,
                            e2.event_id,
                            relation="OCCURRED_BEFORE",
                            time_diff=time_diff,
                            source_type=e1.event_type,
                            target_type=e2.event_type
                        )

    def calculate_interference(
        self,
        event_a_type: str,
        event_b_type: str,
        temporal_window_seconds: Optional[int] = None
    ) -> float:
        """
        Calculates empirical temporal association delta:
        Delta = P(B | A within window) - P(B | NOT A)
        
        Formula:
        P(B | A) = count(customers where A was followed by B in window) / count(customers with A)
        P(B | NOT A) = count(customers with B but NO preceding A in window) / count(customers without A)
        """
        self.build_graph()
        window = temporal_window_seconds or self.temporal_window_seconds
        events = event_bus.get_history()

        if not events:
            return 0.0

        # Group events by customer
        customer_events: Dict[str, List[DomainEvent]] = {}
        for e in events:
            customer_events.setdefault(e.customer_id, []).append(e)

        customers_with_a = 0
        customers_with_a_and_b = 0
        customers_without_a = 0
        customers_without_a_with_b = 0

        for cust_id, cust_evts in customer_events.items():
            sorted_evts = sorted(cust_evts, key=lambda x: x.timestamp)
            a_events = [e for e in sorted_evts if e.event_type == event_a_type]
            b_events = [e for e in sorted_evts if e.event_type == event_b_type]

            if a_events:
                customers_with_a += 1
                # Check if any A is followed by B within temporal window
                has_a_followed_by_b = False
                for a_e in a_events:
                    for b_e in b_events:
                        if 0 <= (b_e.timestamp - a_e.timestamp) <= window:
                            has_a_followed_by_b = True
                            break
                    if has_a_followed_by_b:
                        break
                if has_a_followed_by_b:
                    customers_with_a_and_b += 1
            else:
                customers_without_a += 1
                if b_events:
                    customers_without_a_with_b += 1

        # Check sample size threshold
        if customers_with_a < self.min_sample_size:
            return 0.0

        p_b_given_a = customers_with_a_and_b / customers_with_a if customers_with_a > 0 else 0.0
        p_b_given_not_a = customers_without_a_with_b / customers_without_a if customers_without_a > 0 else 0.0

        association_delta = p_b_given_a - p_b_given_not_a
        return round(association_delta, 4)

    def get_graph_data(self, customer_id: str) -> Dict[str, List[Any]]:
        self.build_graph()
        nodes = []
        for n, d in self.graph.nodes(data=True):
            if d.get("customer_id") == customer_id:
                nodes.append({
                    "id": n,
                    "type": d.get("event_type"),
                    "timestamp": d.get("timestamp"),
                    "state": d.get("new_state")
                })

        node_ids = {n["id"] for n in nodes}
        edges = []
        for u, v, d in self.graph.edges(data=True):
            if u in node_ids and v in node_ids:
                edges.append({
                    "source": u,
                    "target": v,
                    "relation": d.get("relation"),
                    "time_diff": d.get("time_diff")
                })

        return {"nodes": nodes, "edges": edges}

interference_engine = RevenueInterferenceEngine()
