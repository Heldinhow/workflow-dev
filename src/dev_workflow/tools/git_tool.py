"""Custom Git tool for repository operations."""

import subprocess
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GitCommandInput(BaseModel):
    subcommand: str = Field(
        ...,
        description=(
            "Git subcommand and arguments. Examples: "
            "'status', 'add -A', 'commit -m \"feat: add auth\"', "
            "'checkout -b feature/auth', 'push origin HEAD', "
            "'diff HEAD', 'log --oneline -10'"
        ),
    )
    repo_path: str = Field(".", description="Path to the git repository root.")


class GitTool(BaseTool):
    name: str = "Git Operations"
    description: str = (
        "Execute git commands in a repository. Use for: checking status (status), "
        "staging files (add), committing (commit), creating branches (checkout -b), "
        "pushing (push), viewing diffs (diff), reading history (log), "
        "and creating pull requests via 'gh pr create'."
    )
    args_schema: Type[BaseModel] = GitCommandInput

    def _run(self, subcommand: str, repo_path: str = ".") -> str:
        try:
            result = subprocess.run(
                f"git {subcommand}",
                shell=True,
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=30,
            )
            return (
                f"Exit code: {result.returncode}\n"
                f"Output:\n{result.stdout or '(empty)'}\n"
                f"Errors:\n{result.stderr or '(empty)'}"
            )
        except subprocess.TimeoutExpired:
            return f"ERROR: Git command timed out: git {subcommand}"
        except Exception as e:
            return f"ERROR: {str(e)}"
