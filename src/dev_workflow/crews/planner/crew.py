"""Planner Crew — creates a detailed implementation plan."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool


def _llm(temperature: float = 0.3) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'minimax-m2.7-highspeed')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1"),
        temperature=temperature,
    )


@CrewBase
class PlannerCrew:
    """Planner crew — reads YAML configs from ./config/."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config["planner"],
            llm=_llm(temperature=0.3),
            tools=[FileReadTool(), FileWriterTool(), DirectoryReadTool()],
            verbose=True,
            max_iter=15,
        )

    @task
    def plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["plan_task"],
            agent=self.planner(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
