"""Executor Crew — implements the code based on the plan."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool
from dev_workflow.tools import ShellTool


def _llm(temperature: float = 0.2) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'minimax-m2.7-highspeed')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1"),
        temperature=temperature,
    )


@CrewBase
class ExecutorCrew:
    """Executor crew — reads YAML configs from ./config/."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def executor(self) -> Agent:
        return Agent(
            config=self.agents_config["executor"],
            llm=_llm(temperature=0.2),
            tools=[
                FileReadTool(),
                FileWriterTool(),
                DirectoryReadTool(),
                ShellTool(),
            ],
            verbose=True,
            max_iter=30,
            max_retry_limit=3,
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config["coding_task"],
            agent=self.executor(),
            guardrails=[
                "All implemented functions must have docstrings",
                "No hardcoded secrets, passwords, or API keys in the code",
                "All files specified in the plan must be created",
            ],
            guardrail_max_retries=3,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,  # remembers failed approaches across retry iterations
        )
