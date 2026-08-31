from typing import List
from backend.missions.models import Mission, MissionStatus

class MetricsEngine:
    def __init__(self):
        self.missions: List[Mission] = []
        
    def track_mission(self, mission: Mission):
        self.missions.append(mission)
        
    def get_stats(self):
        total = len(self.missions)
        completed = sum(1 for m in self.missions if m.status == MissionStatus.COMPLETED)
        escalated = sum(1 for m in self.missions if m.status == MissionStatus.ESCALATED)
        
        target_revenue = sum(m.goal.target for m in self.missions)
        recovered = sum(m.recovered_amount for m in self.missions)
        
        recovery_rate = (recovered / target_revenue * 100) if target_revenue > 0 else 0
        
        return {
            "total_missions": total,
            "completed": completed,
            "escalated": escalated,
            "target_revenue": target_revenue,
            "recovered_revenue": recovered,
            "recovery_rate_percent": round(recovery_rate, 2)
        }

metrics_engine = MetricsEngine()
