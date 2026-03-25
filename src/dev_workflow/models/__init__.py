"""SQLModel models for persistent execution storage."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class ExecutionPhase(SQLModel, table=True):
    __tablename__ = "execution_phases"

    id: Optional[int] = Field(default=None, primary_key=True)
    execution_id: str = Field(foreign_key="executions.id", index=True)
    name: str = Field(index=True)
    label: str
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: Optional[str] = None

    execution: Optional["Execution"] = Relationship(
        sa_relationship_kwargs={"viewonly": True}
    )


class Execution(SQLModel, table=True):
    __tablename__ = "executions"

    id: str = Field(primary_key=True)
    feature_request: str
    project_path: str
    status: str = "pending"
    current_phase: Optional[str] = None
    current_agent: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    test_retry_count: int = 0
    max_test_retries: int = 3
    errors: str = "[]"
    log: str = "[]"
    token_usage: str = "{}"
    cancelled_at: Optional[str] = None
    github_pr_url: Optional[str] = None
    github_branch: Optional[str] = None
    linear_issue_id: Optional[str] = None
    linear_issue_url: Optional[str] = None
    workspace_mode: str = "sandbox"
    github_repo: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    phases: list["ExecutionPhase"] = Relationship(back_populates="execution")
