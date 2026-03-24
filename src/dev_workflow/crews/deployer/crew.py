"""Deployer Crew — commits, creates PR, and deploys the validated code."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool
from dev_workflow.tools import ShellTool, GitTool


def _llm(temperature: float = 0.1) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'minimax-m2.7-highspeed')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1"),
        temperature=temperature,
    )


@CrewBase
class DeployerCrew:
    """Deployer crew — reads YAML configs from ./config/."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def deployer(self) -> Agent:
        return Agent(
            config=self.agents_config["deployer"],
            llm=_llm(temperature=0.1),
            tools=[ShellTool(), GitTool(), FileReadTool()],
            verbose=True,
            max_iter=20,
        )

    @task
    def deploy_task(self) -> Task:
        return Task(
            config=self.tasks_config["deploy_task"],
            agent=self.deployer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
