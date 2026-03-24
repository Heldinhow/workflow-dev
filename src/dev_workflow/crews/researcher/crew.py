"""Researcher Crew — gathers technical context before implementation."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import BraveSearchTool, ScrapeWebsiteTool, FileReadTool, DirectoryReadTool


def _llm(temperature: float = 0.5) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'minimax-m2.7-highspeed')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1"),
        temperature=temperature,
    )


@CrewBase
class ResearcherCrew:
    """Researcher crew — reads YAML configs from ./config/."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            llm=_llm(temperature=0.5),
            tools=[
                BraveSearchTool(api_key=os.getenv("BRAVE_API_KEY")),
                ScrapeWebsiteTool(),
                FileReadTool(),
                DirectoryReadTool(),
            ],
            verbose=True,
            max_iter=15,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.researcher(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
