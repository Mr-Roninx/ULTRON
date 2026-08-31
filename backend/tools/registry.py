from backend.tools.investigation import investigation_tools
from backend.tools.decision import decision_tools
from backend.tools.execution import execution_tools

class ToolRegistry:
    def __init__(self):
        self.investigation = investigation_tools
        self.decision = decision_tools
        self.execution = execution_tools
        
    # We could expose specific tool routing here if needed by the LLM function calling schema

registry = ToolRegistry()
