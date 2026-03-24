"""Reviewer Crew — performs code review and returns a structured ReviewOutput."""

import os
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, DirectoryReadTool
from dev_workflow.tools import ShellTool
from dev_workflow import emitter as _emit


def _llm(temperature: float = 0.1) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'minimax-m2.7-highspeed')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.io/v1"),
        temperature=temperature,
    )


class ReviewOutput(BaseModel):
    """
    Structured review result — pattern from self_evaluation_loop_flow.
    The Flow's @router reads review.passed (bool) for reliable routing.
    """
    passed: bool
    severity: str        # "none" | "minor" | "major" | "critical"
    issues: list[str]
    feedback: str        # Actionable summary forwarded to the executor


@CrewBase
class ReviewerCrew:
    """Reviewer crew — reads YAML configs from ./config/."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    execution_id: str = ""

    def _step_callback(self, step_output) -> None:
        try:
            if hasattr(step_output, 'output'):
                msg = str(step_output.output)[:300]
            elif hasattr(step_output, 'return_values'):
                msg = str(step_output.return_values.get('output', step_output))[:300]
            else:
                msg = str(step_output)[:300]
            msg = msg.strip()
            if msg and self.execution_id:
                _emit.emit(self.execution_id, "agent_step", "review", msg)
        except Exception:
            pass

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["reviewer"],
            llm=_llm(temperature=0.1),
            tools=[FileReadTool(), DirectoryReadTool(), ShellTool()],
            verbose=True,
            max_iter=20,
            step_callback=self._step_callback,
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config["review_task"],
            agent=self.reviewer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
