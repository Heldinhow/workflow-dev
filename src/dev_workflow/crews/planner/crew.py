"""Planner Crew — creates a detailed implementation plan."""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool
from dev_workflow import emitter as _emit


def _llm(temperature: float = 0.3) -> LLM:
    from dev_workflow.interceptor import MiniMaxInterceptor

    return LLM(
        model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.1"),
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.io/v1"),
        temperature=temperature,
        interceptor=MiniMaxInterceptor(),
    )


@CrewBase
class PlannerCrew:
    """Planner crew — reads YAML configs from ./config/."""

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
                _emit.emit(self.execution_id, "agent_step", "planning", msg)
        except Exception:
            pass

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config["planner"],
            llm=_llm(temperature=0.3),
            tools=[DirectoryReadTool()],
            verbose=True,
            max_iter=15,
            step_callback=self._step_callback,
        )


@CrewBase
class PlannerCrew:
    """Planner crew — reads YAML configs from ./config/."""

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
                _emit.emit(self.execution_id, "agent_step", "planning", msg)
        except Exception:
            pass

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config["planner"],
            llm=_llm(temperature=0.3),
            tools=[],
            verbose=True,
            max_iter=15,
            step_callback=self._step_callback,
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
