"""GitHub API integration tool for creating branches, commits, and PRs."""

import os
from typing import Optional
from crewai.tools import BaseTool


class GitHubTool(BaseTool):
    name: str = "GitHub Integration"
    description: str = "Create GitHub branches, commits, and pull requests"

    def run(
        self,
        action: str,
        **kwargs,
    ) -> dict:
        """
        Perform GitHub actions.

        Args:
            action: The action to perform (create_branch, commit_files, create_pr)
            branch_name: Name for the new branch
            repo: Repository in format 'owner/repo'
            message: Commit message
            files: Dict of filename -> content to commit
            title: PR title
            body: PR body
            base: Base branch for PR (default: main)
        """
        if action == "create_branch":
            return self._create_branch(
                kwargs.get("branch_name"),
                kwargs.get("repo"),
            )
        elif action == "commit_files":
            return self._commit_files(
                kwargs.get("branch_name"),
                kwargs.get("repo"),
                kwargs.get("message"),
                kwargs.get("files", {}),
            )
        elif action == "create_pr":
            return self._create_pr(
                kwargs.get("branch_name"),
                kwargs.get("repo"),
                kwargs.get("title"),
                kwargs.get("body", ""),
                kwargs.get("base", "main"),
            )
        else:
            return {"error": f"Unknown action: {action}"}

    def _create_branch(self, branch_name: str, repo: str) -> dict:
        """Create a new branch."""
        import subprocess

        if not branch_name or not repo:
            return {"error": "branch_name and repo are required"}

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return {"error": "GITHUB_TOKEN not configured"}

        try:
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                text=True,
                cwd=f"/tmp/{repo.split('/')[1]}",
            )
            if result.returncode == 0:
                return {"success": True, "branch": branch_name}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def _commit_files(
        self,
        branch_name: str,
        repo: str,
        message: str,
        files: dict,
    ) -> dict:
        """Commit files to a branch."""
        import subprocess
        import os

        if not all([branch_name, repo, message, files]):
            return {"error": "branch_name, repo, message, and files are required"}

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return {"error": "GITHUB_TOKEN not configured"}

        work_dir = f"/tmp/{repo.split('/')[1]}"

        try:
            for filename, content in files.items():
                filepath = os.path.join(work_dir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w") as f:
                    f.write(content)

            subprocess.run(["git", "add", "."], cwd=work_dir, check=True)
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=work_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return {"success": True, "commit": message}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def _create_pr(
        self,
        branch_name: str,
        repo: str,
        title: str,
        body: str = "",
        base: str = "main",
    ) -> dict:
        """Create a pull request."""
        import subprocess

        if not all([branch_name, repo, title]):
            return {"error": "branch_name, repo, and title are required"}

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return {"error": "GITHUB_TOKEN not configured"}

        work_dir = f"/tmp/{repo.split('/')[1]}"

        try:
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name], cwd=work_dir, check=True
            )

            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body or title,
                    "--base",
                    base,
                ],
                cwd=work_dir,
                capture_output=True,
                text=True,
                env={**os.environ, "GH_TOKEN": token},
            )

            if result.returncode == 0:
                pr_url = result.stdout.strip()
                return {"success": True, "pr_url": pr_url}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
