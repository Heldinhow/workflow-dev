"""Shared state for the Dev Workflow Flow."""

from pydantic import BaseModel, Field
from datetime import datetime


class DevWorkflowState(BaseModel):
    # Input
    feature_request: str = ""
    project_path: str = "./output"

    # Phase outputs
    research_findings: str = ""
    implementation_plan: str = ""
    code_summary: str = ""
    review_feedback: str = ""
    test_results: str = ""
    deployment_output: str = ""

    # Loop control
    retry_count: int = 0
    max_retries: int = 3
    test_retry_count: int = 0
    max_test_retries: int = 3

    # Status flags
    review_passed: bool = False
    tests_passed: bool = False
    deploy_succeeded: bool = False

    # API observability — empty string means CLI mode (no events emitted)
    execution_id: str = ""

    # Audit trail
    errors: list[str] = Field(default_factory=list)
    timestamps: dict = Field(default_factory=dict)

    def log_phase(self, phase: str) -> None:
        self.timestamps[phase] = datetime.now().isoformat()
