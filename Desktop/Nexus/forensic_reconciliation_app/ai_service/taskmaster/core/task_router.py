"""
Task Router Component
"""
from typing import Dict, Any, List, Optional
from ..models.agent import Agent
from ..models.job import Job

class TaskRouter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, Agent] = {}

    async def start(self):
        pass

    async def stop(self):
        pass

    async def register_agent(self, agent: Agent):
        self.agents[agent.agent_id] = agent

    async def find_agent_for_job(self, job: "Job") -> Optional[Agent]:
        for agent in self.agents.values():
            if job.job_type.value in agent.capabilities:
                return agent
        return None

    async def get_health(self) -> Dict[str, Any]:
        return {"healthy": True}

    async def get_metrics(self) -> Dict[str, Any]:
        return {"registered_agents": len(self.agents)}
