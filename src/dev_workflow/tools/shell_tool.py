"""Custom Shell execution tool for running tests, linters, and build commands."""

import shlex
import subprocess
from typing import Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ShellCommandInput(BaseModel):
    command: str = Field(
        ..., description="The shell command to execute (e.g. 'pytest -v', 'npm test')"
    )
    working_dir: Optional[str] = Field(
        None, description="Working directory path. Defaults to CWD."
    )
    timeout: int = Field(
        60, description="Timeout in seconds before the command is killed."
    )


class ShellTool(BaseTool):
    name: str = "Shell Command Executor"
    description: str = (
        "Execute shell commands on the host machine. Use for: running tests (pytest, npm test, "
        "cargo test), linters (flake8, eslint, mypy), build commands (npm run build, make), "
        "package managers (pip install, npm install), or any CLI tool. "
        "Returns stdout, stderr, and exit code."
    )
    args_schema: Type[BaseModel] = ShellCommandInput

    def _run(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: int = 60,
    ) -> str:
        try:
            result = subprocess.run(
                shlex.split(command),
                shell=False,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=timeout,
            )
            output = (
                f"Exit code: {result.returncode}\n"
                f"--- STDOUT ---\n{result.stdout or '(empty)'}\n"
                f"--- STDERR ---\n{result.stderr or '(empty)'}"
            )
            return output
        except subprocess.TimeoutExpired:
            return f"ERROR: Command timed out after {timeout}s: {command}"
        except Exception as e:
            return f"ERROR executing command '{command}': {str(e)}"
