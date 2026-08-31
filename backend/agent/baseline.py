from backend.missions.models import Mission, MissionStatus
from backend.agent.execution import executor
from financial.authority import AuthorityLevel

class BaselineAgent:
    def __init__(self, mission: Mission):
        self.mission = mission
        
    def run(self, context: dict):
        print(f"[BASELINE AGENT] Starting mission {self.mission.mission_id}")
        print("[BASELINE AGENT] Executing pre-programmed rule: If invoice is overdue, send reminder.")
        
        # Blindly send reminder
        intent = {"action_type": "SEND_INVOICE_REMINDER", "payload": {}}
        result = executor.execute_action(
            self.mission.mission_id, 
            context, 
            intent, 
            self.mission.constraints.max_risk, 
            AuthorityLevel(self.mission.authority)
        )
        
        if result["status"] == "SUCCESS":
            # Baseline agent assumes success and stops.
            print("[BASELINE AGENT] Reminder sent. Assuming success.")
            # If it actually failed to recover the money in the real world, it wouldn't know or care,
            # or it would just mark the mission as complete anyway.
            self.mission.status = MissionStatus.COMPLETED
        else:
            print(f"[BASELINE AGENT] Failed: {result['reason']}")
            self.mission.status = MissionStatus.FAILED
            
baseline_agent = BaselineAgent
