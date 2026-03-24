"""Executor Crew — implements the code based on the plan."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool
from dev_workflow.tools import ShellTool
from dev_workflow import emitter as _emit


def _llm(temperature: float = 0.2) -> LLM:
    return LLM(
        model=f"minimax/{os.getenv('MINIMAX_MODEL', 'minimax-m2.7-highspeed')}",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.io/v1"),
        temperature=temperature,
    )


@CrewBase
class ExecutorCrew:
    """Executor crew — reads YAML configs from ./config/."""

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
                _emit.emit(self.execution_id, "agent_step", "execution", msg)
        except Exception:
            pass

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
            step_callback=self._step_callback,
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config["coding_task"],
            agent=self.executor(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
        )
