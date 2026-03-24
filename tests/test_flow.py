"""
Tests for DevWorkflowFlow routing and feedback loops.

Strategy: mock all 6 Crew.kickoff() calls — zero real LLM calls.
Each test scenario exercises a different routing path through the flow.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from dev_workflow.flow import DevWorkflowFlow
from dev_workflow.crews.reviewer.crew import ReviewOutput
from dev_workflow.crews.tester.crew import TestOutput


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _crew_result(raw: str = "OK", pydantic=None) -> MagicMock:
    r = MagicMock()
    r.raw = raw
    r.pydantic = pydantic
    return r


def _review(
    passed: bool, issues: list[str] | None = None, feedback: str = ""
) -> ReviewOutput:
    return ReviewOutput(
        passed=passed,
        severity="none" if passed else "major",
        issues=issues or ([] if passed else ["Issue found"]),
        feedback=feedback or ("LGTM" if passed else "Fix the issues listed above."),
    )


def _tests(
    passed: bool, failed: int = 0, failures: list[str] | None = None
) -> TestOutput:
    return TestOutput(
        passed=passed,
        total_tests=10,
        failed_tests=failed,
        failures=failures or ([] if passed else ["test_foo: AssertionError"]),
        coverage=95.0 if passed else 55.0,
        feedback="All passing." if passed else "Fix the failing tests.",
    )


def _setup(
    mock_cls, *, raw: str = "OK", pydantic=None, side_effects: list | None = None
):
    """Wire MockClass().crew().kickoff() → result."""
    instance = MagicMock()
    mock_cls.return_value = instance
    kickoff = instance.crew.return_value.kickoff
    if side_effects:
        kickoff.side_effect = side_effects
    else:
        kickoff.return_value = _crew_result(raw=raw, pydantic=pydantic)
    return kickoff


P = "dev_workflow.flow"


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Happy path: no retries, all phases succeed
# ─────────────────────────────────────────────────────────────────────────────


@patch(f"{P}.DeployerCrew")
@patch(f"{P}.TesterCrew")
@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
@patch(f"{P}.PlannerCrew")
@patch(f"{P}.ResearcherCrew")
def test_happy_path(m_res, m_plan, m_exec, m_rev, m_test, m_dep):
    """Full flow, no retries. All 6 phases run exactly once."""
    _setup(m_res, raw="research findings")
    _setup(m_plan, raw="implementation plan")
    _setup(m_exec, raw="code written")
    _setup(m_rev, pydantic=_review(passed=True))
    _setup(m_test, pydantic=_tests(passed=True))
    _setup(m_dep, raw="PR #42 created")

    flow = DevWorkflowFlow()
    flow.kickoff(
        inputs={"feature_request": "Add hello endpoint", "project_path": "./output"}
    )

    s = flow.state
    assert s.review_passed, "Review should pass"
    assert s.tests_passed, "Tests should pass"
    assert s.deploy_succeeded, "Deploy should succeed"
    assert s.retry_count == 1, "Executor ran exactly once"
    assert s.errors == [], "No errors"
    assert "deploy_end" in s.timestamps

    assert m_exec.return_value.crew.return_value.kickoff.call_count == 1
    assert m_rev.return_value.crew.return_value.kickoff.call_count == 1
    assert m_test.return_value.crew.return_value.kickoff.call_count == 1
    assert m_dep.return_value.crew.return_value.kickoff.call_count == 1


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Review fails once, then passes
# ─────────────────────────────────────────────────────────────────────────────


@patch(f"{P}.DeployerCrew")
@patch(f"{P}.TesterCrew")
@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
@patch(f"{P}.PlannerCrew")
@patch(f"{P}.ResearcherCrew")
def test_review_loop_one_retry(m_res, m_plan, m_exec, m_rev, m_test, m_dep):
    """Reviewer fails on attempt 1, passes on attempt 2. Executor runs twice."""
    _setup(m_res, raw="research")
    _setup(m_plan, raw="plan")
    _setup(m_exec, raw="code")
    _setup(
        m_rev,
        side_effects=[
            _crew_result(
                pydantic=_review(passed=False, feedback="Missing error handling")
            ),
            _crew_result(pydantic=_review(passed=True)),
        ],
    )
    _setup(m_test, pydantic=_tests(passed=True))
    _setup(m_dep, raw="deployed")

    flow = DevWorkflowFlow()
    flow.kickoff(
        inputs={"feature_request": "Add user auth", "project_path": "./output"}
    )

    s = flow.state
    assert s.review_passed
    assert s.tests_passed
    assert s.deploy_succeeded
    assert s.retry_count == 2, "Executor ran twice (original + 1 recode)"
    assert s.errors == []

    assert m_exec.return_value.crew.return_value.kickoff.call_count == 2
    assert m_rev.return_value.crew.return_value.kickoff.call_count == 2
    assert m_dep.return_value.crew.return_value.kickoff.call_count == 1


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Tests fail once, then pass (triggers an executor fix cycle)
# ─────────────────────────────────────────────────────────────────────────────


@patch(f"{P}.DeployerCrew")
@patch(f"{P}.TesterCrew")
@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
@patch(f"{P}.PlannerCrew")
@patch(f"{P}.ResearcherCrew")
def test_test_loop_one_retry(m_res, m_plan, m_exec, m_rev, m_test, m_dep):
    """Tests fail once → executor fix → review passes → tests pass."""
    _setup(m_res, raw="research")
    _setup(m_plan, raw="plan")
    _setup(m_exec, raw="code")
    _setup(
        m_rev,
        side_effects=[
            _crew_result(pydantic=_review(passed=True)),  # initial review
            _crew_result(pydantic=_review(passed=True)),  # review after test-fix recode
        ],
    )
    _setup(
        m_test,
        side_effects=[
            _crew_result(pydantic=_tests(passed=False, failed=2)),
            _crew_result(pydantic=_tests(passed=True)),
        ],
    )
    _setup(m_dep, raw="deployed")

    flow = DevWorkflowFlow()
    flow.kickoff(
        inputs={"feature_request": "Add JWT tokens", "project_path": "./output"}
    )

    s = flow.state
    assert s.tests_passed
    assert s.deploy_succeeded
    assert s.retry_count == 2, "Executor ran twice (original + fix for tests)"
    assert s.test_retry_count == 2, "Tester ran twice"
    assert s.errors == []


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — Review escalation: reviewer always fails, max_retries exhausted
# Tested by calling execution_and_review_loop directly (avoids the CrewAI async
# engine's event loop which can't terminate "escalate" emitted inside asyncio.gather)
# ─────────────────────────────────────────────────────────────────────────────


@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
def test_review_escalation(m_exec, m_rev):
    """Reviewer always fails. After max_retries the loop sets errors and returns."""
    _setup(m_exec, raw="code")
    _setup(
        m_rev,
        side_effects=[
            _crew_result(pydantic=_review(passed=False, feedback="Critical bug"))
            for _ in range(10)
        ],
    )

    flow = DevWorkflowFlow()
    flow.state.feature_request = "Broken feature"
    flow.state.implementation_plan = "plan"
    flow.state.project_path = "./output"

    # Call the loop method directly — no kickoff needed
    flow.execution_and_review_loop()

    s = flow.state
    assert not s.review_passed, "Review must have failed"
    assert s.retry_count == s.max_retries, "Must have retried exactly max_retries times"
    assert len(s.errors) > 0, "Must record the escalation error"
    assert "escalated" in s.timestamps, "Must log the escalation timestamp"
    assert "Critical bug" in s.errors[0]  # Error message must include reviewer feedback

    # Verify router would send to escalate
    route = flow.route_after_review()
    assert route == "escalate"


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — Test escalation: tests always fail, max_test_retries exhausted
# ─────────────────────────────────────────────────────────────────────────────


@patch(f"{P}.TesterCrew")
@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
def test_test_escalation(m_exec, m_rev, m_test):
    """Review always passes, tests always fail. Loop escalates after max_test_retries."""
    _setup(m_exec, raw="code")
    _setup(
        m_rev,
        side_effects=[_crew_result(pydantic=_review(passed=True)) for _ in range(20)],
    )
    _setup(
        m_test,
        side_effects=[
            _crew_result(pydantic=_tests(passed=False, failed=3)) for _ in range(20)
        ],
    )

    flow = DevWorkflowFlow()
    flow.state.feature_request = "Flaky tests"
    flow.state.implementation_plan = "plan"
    flow.state.project_path = "./output"

    # First: execution + review must pass to reach testing
    flow.execution_and_review_loop()
    assert flow.state.review_passed, "Review should pass (precondition for testing)"

    # Now run the test loop
    flow.testing_and_fix_loop()

    s = flow.state
    assert not s.tests_passed, "Tests must have failed"
    assert s.test_retry_count == s.max_test_retries, (
        "Must retry exactly max_test_retries times"
    )
    assert len(s.errors) > 0, "Must record the escalation error"
    assert "escalated" in s.timestamps

    # Verify router would send to escalate
    route = flow.route_after_tests()
    assert route == "escalate"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — Review feedback is forwarded to executor on retry
# ─────────────────────────────────────────────────────────────────────────────


@patch(f"{P}.DeployerCrew")
@patch(f"{P}.TesterCrew")
@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
@patch(f"{P}.PlannerCrew")
@patch(f"{P}.ResearcherCrew")
def test_feedback_forwarded_to_executor(m_res, m_plan, m_exec, m_rev, m_test, m_dep):
    """Review feedback must appear in executor's inputs on the retry call."""
    _setup(m_res, raw="research output")
    _setup(m_plan, raw="plan output")
    _setup(m_exec, raw="code output")
    _setup(
        m_rev,
        side_effects=[
            _crew_result(
                pydantic=_review(passed=False, feedback="Add input validation")
            ),
            _crew_result(pydantic=_review(passed=True)),
        ],
    )
    _setup(m_test, pydantic=_tests(passed=True))
    _setup(m_dep, raw="deployed")

    flow = DevWorkflowFlow()
    flow.kickoff(inputs={"feature_request": "Add endpoint", "project_path": "./output"})

    kickoff_calls = m_exec.return_value.crew.return_value.kickoff.call_args_list
    assert len(kickoff_calls) == 2, "Executor must have been called twice"

    second_inputs = kickoff_calls[1].kwargs["inputs"]
    assert "Add input validation" in second_inputs["reviewer_feedback"], (
        "Review feedback must be forwarded to executor on retry"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — _parse_review rejects tool call JSON
# ─────────────────────────────────────────────────────────────────────────────


def test_parse_review_rejects_tool_call_json():
    """_parse_review must detect and reject tool call JSON format."""
    flow = DevWorkflowFlow()

    tool_call_json = (
        '{"tool": "list_files_in_directory", "args": {"--directory": "./output"}}'
    )
    result = flow._parse_review(tool_call_json)

    assert result["passed"] == False, "Tool call JSON should be rejected"
    assert "Malformed review output" in result["feedback"], (
        "Should indicate parsing error"
    )


def test_parse_review_accepts_valid_json():
    """_parse_review must accept valid ReviewOutput JSON."""
    flow = DevWorkflowFlow()

    valid_json = (
        '{"passed": true, "severity": "none", "issues": [], "feedback": "LGTM"}'
    )
    result = flow._parse_review(valid_json)

    assert result["passed"] == True
    assert result["severity"] == "none"
    assert result["feedback"] == "LGTM"
