"""Researcher Crew — gathers technical context before implementation."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import (
    BraveSearchTool,
    ScrapeWebsiteTool,
    FileReadTool,
    DirectoryReadTool,
)
from dev_workflow import emitter as _emit


def _llm(temperature: float = 0.5) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'MiniMax-M2.1')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.io/v1"),
        temperature=temperature,
    )


@CrewBase
class ResearcherCrew:
    """Researcher crew — reads YAML configs from ./config/."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    execution_id: str = ""

    def _step_callback(self, step_output) -> None:
        try:
            if hasattr(step_output, "output"):
                msg = str(step_output.output)[:300]
            elif hasattr(step_output, "return_values"):
                msg = str(step_output.return_values.get("output", step_output))[:300]
            else:
                msg = str(step_output)[:300]
            msg = msg.strip()
            if msg and self.execution_id:
                _emit.emit(self.execution_id, "agent_step", "research", msg)
        except Exception:
            pass

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
            step_callback=self._step_callback,
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
