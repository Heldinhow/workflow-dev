"""Tester Crew — runs tests and returns a structured TestOutput."""

import os
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool
from dev_workflow.tools import ShellTool
from dev_workflow import emitter as _emit


def _llm(temperature: float = 0.1) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'MiniMax-M2.1')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.io/v1"),
        temperature=temperature,
    )


class TestOutput(BaseModel):
    """
    Structured test result — pattern from self_evaluation_loop_flow.
    The Flow's @router reads tests.passed (bool) for reliable routing.
    """

    passed: bool
    total_tests: int
    failed_tests: int
    failures: list[str]  # Each item: "test_name: error message"
    coverage: float  # 0.0 to 100.0
    feedback: str  # Actionable summary forwarded to the executor


@CrewBase
class TesterCrew:
    """Tester crew — reads YAML configs from ./config/."""

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
                _emit.emit(self.execution_id, "agent_step", "testing", msg)
        except Exception:
            pass

    @agent
    def tester(self) -> Agent:
        return Agent(
            config=self.agents_config["tester"],
            llm=_llm(temperature=0.1),
            tools=[
                ShellTool(),
                FileReadTool(),
                FileWriterTool(),
                DirectoryReadTool(),
            ],
            verbose=True,
            max_iter=25,
            step_callback=self._step_callback,
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_task"],
            agent=self.tester(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
