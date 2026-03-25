"""Linear API integration tool for creating and updating issues."""

import os
import requests
from typing import Optional, ClassVar
from crewai.tools import BaseTool


class LinearTool(BaseTool):
    name: str = "Linear Issue Tracker"
    description: str = "Create and update Linear issues"

    LINEAR_API_URL: ClassVar[str] = "https://api.linear.app/graphql"

    def run(
        self,
        action: str,
        **kwargs,
    ) -> dict:
        """
        Perform Linear actions.

        Args:
            action: The action to perform (create_issue, update_status, add_comment)
            team_id: Linear team ID
            title: Issue title
            description: Issue description
            issue_id: Linear issue ID
            state: New state (e.g., 'In Progress', 'Done')
            body: Comment body
        """
        if action == "create_issue":
            return self._create_issue(
                kwargs.get("team_id"),
                kwargs.get("title"),
                kwargs.get("description", ""),
            )
        elif action == "update_status":
            return self._update_status(
                kwargs.get("issue_id"),
                kwargs.get("state"),
            )
        elif action == "add_comment":
            return self._add_comment(
                kwargs.get("issue_id"),
                kwargs.get("body"),
            )
        else:
            return {"error": f"Unknown action: {action}"}

    def _headers(self) -> dict:
        """Get headers for Linear API."""
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            raise ValueError("LINEAR_API_KEY not configured")
        return {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

    def _graphql(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query against Linear API."""
        response = requests.post(
            self.LINEAR_API_URL,
            json={"query": query, "variables": variables},
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
        data = response.json()
        if "errors" in data:
            return {"error": data["errors"]}
        return data.get("data", {})

    def _create_issue(
        self,
        team_id: str,
        title: str,
        description: str = "",
    ) -> dict:
        """Create a new Linear issue."""
        if not team_id or not title:
            return {"error": "team_id and title are required"}

        mutation = """
        mutation CreateIssue($teamId: String!, $title: String!, $description: String) {
            issueCreate(input: {
                teamId: $teamId
                title: $title
                description: $description
            }) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                }
            }
        }
        """

        try:
            data = self._graphql(
                mutation,
                {
                    "teamId": team_id,
                    "title": title,
                    "description": description,
                },
            )

            if "error" in data:
                return data

            result = data.get("issueCreate", {})
            if result.get("success"):
                issue = result["issue"]
                return {
                    "success": True,
                    "issue_id": issue["identifier"],
                    "issue_url": issue["url"],
                }
            return {"error": "Failed to create issue"}
        except Exception as e:
            return {"error": str(e)}

    def _update_status(self, issue_id: str, state: str) -> dict:
        """Update issue state."""
        if not issue_id or not state:
            return {"error": "issue_id and state are required"}

        mutation = """
        mutation UpdateIssue($issueId: String!, $state: String!) {
            issueUpdate(id: $issueId, input: {
                stateName: $state
            }) {
                success
            }
        }
        """

        try:
            data = self._graphql(
                mutation,
                {
                    "issueId": issue_id,
                    "state": state,
                },
            )
            if "error" in data:
                return data
            return {"success": data.get("issueUpdate", {}).get("success", False)}
        except Exception as e:
            return {"error": str(e)}

    def _add_comment(self, issue_id: str, body: str) -> dict:
        """Add a comment to an issue."""
        if not issue_id or not body:
            return {"error": "issue_id and body are required"}

        mutation = """
        mutation CreateComment($issueId: String!, $body: String!) {
            commentCreate(input: {
                issueId: $issueId
                body: $body
            }) {
                success
            }
        }
        """

        try:
            data = self._graphql(
                mutation,
                {
                    "issueId": issue_id,
                    "body": body,
                },
            )
            if "error" in data:
                return data
            return {"success": data.get("commentCreate", {}).get("success", False)}
        except Exception as e:
            return {"error": str(e)}
