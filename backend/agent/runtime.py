from backend.agent.loop import AgentLoop
from backend.agent.state_machine import AgentPhase
from simulator.models import Mission, MissionStatus
from backend.agent.circuit_breakers import CircuitBreakerTripped

class AgentRuntime:
    def __init__(self):
        self.active_loops = {}

    def start_mission(self, mission: Mission) -> AgentLoop:
        mission.status = MissionStatus.RUNNING
        loop = AgentLoop(
            customer_id="c_1", # Extract from mission if it had one, for now hardcode or pass as arg
            mission_id=mission.mission_id,
            max_risk=mission.constraints.max_risk,
            authority=mission.authority
        )
        self.active_loops[mission.mission_id] = loop
        return loop

    def run_mission(self, mission: Mission):
        loop = self.start_mission(mission)
        
        while True:
            try:
                phase = loop.tick()
                if phase == AgentPhase.COMPLETE:
                    mission.status = MissionStatus.COMPLETED
                    break
                elif phase == AgentPhase.ESCALATE:
                    mission.status = MissionStatus.ESCALATED
                    break
            except CircuitBreakerTripped:
                mission.status = MissionStatus.FAILED
                break
            except Exception as e:
                mission.status = MissionStatus.FAILED
                print(f"Mission failed with error: {e}")
                break

runtime = AgentRuntime()
