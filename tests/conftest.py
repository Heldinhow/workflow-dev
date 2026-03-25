"""Pytest fixtures for mocking crews, API client, and state."""

import pytest
import json
from unittest.mock import MagicMock, patch

from dev_workflow.state import DevWorkflowState
from dev_workflow.crews.reviewer.crew import ReviewOutput
from dev_workflow.crews.tester.crew import TestOutput


def _crew_result(raw: str = "OK", pydantic=None) -> MagicMock:
    r = MagicMock()
    if pydantic is not None and raw == "OK":
        raw = json.dumps(pydantic.model_dump())
    r.raw = raw
    r.pydantic = pydantic
    return r


@pytest.fixture
def mock_state():
    """Fresh DevWorkflowState for testing."""
    return DevWorkflowState(
        feature_request="Test feature",
        project_path="./test_output",
        execution_id="test-exec-123",
    )


@pytest.fixture
def mock_researcher_crew():
    """Mock ResearcherCrew that returns predefined research findings."""
    with patch("dev_workflow.flow.ResearcherCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            raw="Research findings: context gathered about the feature."
        )
        yield mock


@pytest.fixture
def mock_planner_crew():
    """Mock PlannerCrew that returns a predefined implementation plan."""
    with patch("dev_workflow.flow.PlannerCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            raw="Implementation plan: step 1, step 2, step 3."
        )
        yield mock


@pytest.fixture
def mock_executor_crew():
    """Mock ExecutorCrew that returns predefined code summary."""
    with patch("dev_workflow.flow.ExecutorCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            raw="Code written: created app.py with hello endpoint."
        )
        yield mock


@pytest.fixture
def mock_reviewer_crew():
    """Mock ReviewerCrew that returns a passing review."""
    with patch("dev_workflow.flow.ReviewerCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            pydantic=ReviewOutput(
                passed=True,
                severity="none",
                issues=[],
                feedback="LGTM",
            )
        )
        yield mock


@pytest.fixture
def mock_tester_crew():
    """Mock TesterCrew that returns passing tests."""
    with patch("dev_workflow.flow.TesterCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            pydantic=TestOutput(
                passed=True,
                total_tests=10,
                failed_tests=0,
                failures=[],
                coverage=95.0,
                feedback="All tests passing.",
            )
        )
        yield mock


@pytest.fixture
def mock_deployer_crew():
    """Mock DeployerCrew that returns deployment success."""
    with patch("dev_workflow.flow.DeployerCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            raw="PR #42 created. Deployment successful."
        )
        yield mock


@pytest.fixture
def mock_all_crews(mock_researcher_crew, mock_planner_crew, mock_executor_crew,
                   mock_reviewer_crew, mock_tester_crew, mock_deployer_crew):
    """Mock all 6 crews together."""
    return {
        "researcher": mock_researcher_crew,
        "planner": mock_planner_crew,
        "executor": mock_executor_crew,
        "reviewer": mock_reviewer_crew,
        "tester": mock_tester_crew,
        "deployer": mock_deployer_crew,
    }


@pytest.fixture
def failing_reviewer_crew():
    """Mock ReviewerCrew that returns a failing review."""
    with patch("dev_workflow.flow.ReviewerCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            pydantic=ReviewOutput(
                passed=False,
                severity="major",
                issues=["Missing error handling"],
                feedback="Add error handling for edge cases.",
            )
        )
        yield mock


@pytest.fixture
def failing_tester_crew():
    """Mock TesterCrew that returns failing tests."""
    with patch("dev_workflow.flow.TesterCrew") as mock:
        instance = MagicMock()
        mock.return_value = instance
        instance.crew.return_value.kickoff.return_value = _crew_result(
            pydantic=TestOutput(
                passed=False,
                total_tests=10,
                failed_tests=2,
                failures=["test_foo: AssertionError", "test_bar: KeyError"],
                coverage=55.0,
                feedback="Fix failing tests.",
            )
        )
        yield mock


@pytest.fixture
def mock_api_store():
    """Mock API store for testing API endpoints."""
    with patch("dev_workflow.api.store") as mock:
        mock.get.return_value = {
            "id": "test-exec-123",
            "feature_request": "Test feature",
            "project_path": "./test_output",
            "status": "running",
            "current_phase": "research",
            "errors": [],
            "log": [],
        }
        mock.list_all.return_value = []
        mock.list_all_filtered.return_value = []
        yield mock


@pytest.fixture
def mock_emitter():
    """Mock emitter module to capture emitted events."""
    with patch("dev_workflow.emitter") as mock:
        events = []
        def capture_event(execution_id, event_type, phase, message, data=None):
            events.append({
                "execution_id": execution_id,
                "type": event_type,
                "phase": phase,
                "message": message,
                "data": data or {},
            })
        mock.emit.side_effect = capture_event
        mock._handlers = []
        yield mock, events
