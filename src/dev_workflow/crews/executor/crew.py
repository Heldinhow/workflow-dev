"""Executor Crew — implements the code based on the plan."""

import json
import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool
from dev_workflow.tools import ShellTool
from dev_workflow import emitter as _emit


def _llm(temperature: float = 0.2) -> LLM:
    from dev_workflow.interceptor import MiniMaxInterceptor

    return LLM(
        model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.1"),
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_API_BASE", "https://api.minimax.io/v1"),
        temperature=temperature,
        interceptor=MiniMaxInterceptor(),
    )


@CrewBase
class ExecutorCrew:
    """Executor crew — reads YAML configs from ./config/."""

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
                _emit.emit(self.execution_id, "agent_step", "execution", msg)
        except Exception:
            pass

    def _task_callback(self, task_output) -> None:
        """Accumulate token usage from task output."""
        try:
            if not self.execution_id:
                return
            token_data = {}
            if hasattr(task_output, "token_usage") and task_output.token_usage:
                tu = task_output.token_usage
                token_data = {
                    "total_tokens": getattr(tu, "total_tokens", 0) or 0,
                    "prompt_tokens": getattr(tu, "prompt_tokens", 0) or 0,
                    "completion_tokens": getattr(tu, "completion_tokens", 0) or 0,
                }
            elif hasattr(task_output, "usage") and task_output.usage:
                u = task_output.usage
                token_data = {
                    "total_tokens": getattr(u, "total_tokens", 0) or 0,
                    "prompt_tokens": getattr(u, "prompt_tokens", 0) or 0,
                    "completion_tokens": getattr(u, "completion_tokens", 0) or 0,
                }
            if token_data.get("total_tokens", 0) > 0:
                self._update_token_usage(token_data)
        except Exception:
            pass

    def _update_token_usage(self, new_tokens: dict) -> None:
        """Update token usage in store."""
        try:
            from dev_workflow.api import store

            ex = store.get(self.execution_id)
            if not ex:
                return
            current = ex.get("token_usage", {})
            if isinstance(current, str):
                current = json.loads(current) if current else {}
            updated = {
                "total_tokens": current.get("total_tokens", 0)
                + new_tokens.get("total_tokens", 0),
                "prompt_tokens": current.get("prompt_tokens", 0)
                + new_tokens.get("prompt_tokens", 0),
                "completion_tokens": current.get("completion_tokens", 0)
                + new_tokens.get("completion_tokens", 0),
            }
            estimated_cost = updated["total_tokens"] * 0.00001
            updated["estimated_cost_usd"] = round(estimated_cost, 6)
            store.update(self.execution_id, token_usage=json.dumps(updated))
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
            callback=self._task_callback,
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
