"""Tests for DevWorkflowState and state transitions."""

from dev_workflow.state import DevWorkflowState


class TestDevWorkflowState:
    """Tests for DevWorkflowState model."""

    def test_state_has_default_values(self):
        """State initializes with correct default values."""
        state = DevWorkflowState()
        assert state.feature_request == ""
        assert state.project_path == "./output"
        assert state.research_findings == ""
        assert state.implementation_plan == ""
        assert state.code_summary == ""
        assert state.review_feedback == ""
        assert state.test_results == ""
        assert state.deployment_output == ""

    def test_state_retry_defaults(self):
        """State has correct default retry settings."""
        state = DevWorkflowState()
        assert state.retry_count == 0
        assert state.max_retries == 3
        assert state.test_retry_count == 0
        assert state.max_test_retries == 3

    def test_state_status_flags_default_to_false(self):
        """Status flags default to False."""
        state = DevWorkflowState()
        assert state.review_passed is False
        assert state.tests_passed is False
        assert state.deploy_succeeded is False

    def test_state_execution_id_empty(self):
        """execution_id is empty string by default (CLI mode)."""
        state = DevWorkflowState()
        assert state.execution_id == ""

    def test_state_errors_is_list(self):
        """errors field is a list."""
        state = DevWorkflowState()
        assert isinstance(state.errors, list)
        assert state.errors == []

    def test_state_timestamps_is_dict(self):
        """timestamps field is a dict."""
        state = DevWorkflowState()
        assert isinstance(state.timestamps, dict)
        assert state.timestamps == {}

    def test_state_log_phase(self):
        """log_phase adds timestamp for given phase."""
        state = DevWorkflowState()
        state.log_phase("research_start")
        assert "research_start" in state.timestamps
        assert isinstance(state.timestamps["research_start"], str)

    def test_state_log_multiple_phases(self):
        """log_phase tracks multiple phase timestamps."""
        state = DevWorkflowState()
        state.log_phase("research_start")
        state.log_phase("research_end")
        state.log_phase("planning_start")
        assert len(state.timestamps) == 3
        assert "research_start" in state.timestamps
        assert "research_end" in state.timestamps
        assert "planning_start" in state.timestamps

    def test_state_set_feature_request(self):
        """State accepts feature_request as input."""
        state = DevWorkflowState(feature_request="Add REST API endpoint")
        assert state.feature_request == "Add REST API endpoint"

    def test_state_set_project_path(self):
        """State accepts project_path as input."""
        state = DevWorkflowState(project_path="/app/src")
        assert state.project_path == "/app/src"

    def test_state_set_execution_id(self):
        """State accepts execution_id."""
        state = DevWorkflowState(execution_id="abc-123")
        assert state.execution_id == "abc-123"

    def test_state_update_research_findings(self):
        """State stores research findings."""
        state = DevWorkflowState()
        state.research_findings = "Found relevant docs about authentication."
        assert state.research_findings == "Found relevant docs about authentication."

    def test_state_update_implementation_plan(self):
        """State stores implementation plan."""
        state = DevWorkflowState()
        state.implementation_plan = "Step 1: Add auth middleware. Step 2: Create routes."
        assert state.implementation_plan == "Step 1: Add auth middleware. Step 2: Create routes."

    def test_state_update_code_summary(self):
        """State stores code summary."""
        state = DevWorkflowState()
        state.code_summary = "Created app.py with 5 endpoints"
        assert state.code_summary == "Created app.py with 5 endpoints"

    def test_state_update_review_feedback(self):
        """State stores review feedback."""
        state = DevWorkflowState()
        state.review_feedback = "Add error handling for edge cases."
        assert state.review_feedback == "Add error handling for edge cases."

    def test_state_update_test_results(self):
        """State stores test results."""
        state = DevWorkflowState()
        state.test_results = "8/10 tests passing, 2 failures in test_auth"
        assert state.test_results == "8/10 tests passing, 2 failures in test_auth"

    def test_state_update_deployment_output(self):
        """State stores deployment output."""
        state = DevWorkflowState()
        state.deployment_output = "PR #42 created, deployed to staging"
        assert state.deployment_output == "PR #42 created, deployed to staging"

    def test_state_review_passed_flag(self):
        """State review_passed flag can be set."""
        state = DevWorkflowState()
        state.review_passed = True
        assert state.review_passed is True

    def test_state_tests_passed_flag(self):
        """State tests_passed flag can be set."""
        state = DevWorkflowState()
        state.tests_passed = True
        assert state.tests_passed is True

    def test_state_deploy_succeeded_flag(self):
        """State deploy_succeeded flag can be set."""
        state = DevWorkflowState()
        state.deploy_succeeded = True
        assert state.deploy_succeeded is True

    def test_state_increment_retry_count(self):
        """retry_count can be incremented."""
        state = DevWorkflowState()
        state.retry_count += 1
        assert state.retry_count == 1
        state.retry_count += 1
        assert state.retry_count == 2

    def test_state_increment_test_retry_count(self):
        """test_retry_count can be incremented."""
        state = DevWorkflowState()
        state.test_retry_count += 1
        assert state.test_retry_count == 1

    def test_state_add_error(self):
        """errors list can have items appended."""
        state = DevWorkflowState()
        state.errors.append("Review failed: missing tests")
        state.errors.append("Tests failed after 3 retries")
        assert len(state.errors) == 2
        assert "Review failed" in state.errors[0]


class TestStateTransitions:
    """Tests for state transitions through workflow phases."""

    def test_research_phase_transition(self):
        """State transitions correctly through research phase."""
        state = DevWorkflowState()
        state.log_phase("research_start")
        state.research_findings = "Technical research complete"
        state.log_phase("research_end")
        assert "research_start" in state.timestamps
        assert "research_end" in state.timestamps
        assert state.research_findings == "Technical research complete"

    def test_planning_phase_transition(self):
        """State transitions correctly through planning phase."""
        state = DevWorkflowState()
        state.log_phase("planning_start")
        state.implementation_plan = "Implementation plan created"
        state.log_phase("planning_end")
        assert "planning_start" in state.timestamps
        assert "planning_end" in state.timestamps
        assert state.implementation_plan == "Implementation plan created"

    def test_execution_phase_transition(self):
        """State transitions correctly through execution phase."""
        state = DevWorkflowState()
        state.log_phase("execution_start_attempt_1")
        state.code_summary = "Code files created"
        state.log_phase("execution_end_attempt_1")
        assert "execution_start_attempt_1" in state.timestamps
        assert "execution_end_attempt_1" in state.timestamps

    def test_review_phase_transition(self):
        """State transitions correctly through review phase."""
        state = DevWorkflowState()
        state.log_phase("review_start_attempt_1")
        state.review_passed = True
        state.review_feedback = "Code looks good"
        state.log_phase("review_end_attempt_1")
        assert "review_start_attempt_1" in state.timestamps
        assert state.review_passed is True

    def test_testing_phase_transition(self):
        """State transitions correctly through testing phase."""
        state = DevWorkflowState()
        state.log_phase("testing_start_attempt_1")
        state.tests_passed = True
        state.test_results = "All 10 tests passing"
        state.log_phase("testing_end_attempt_1")
        assert "testing_start_attempt_1" in state.timestamps
        assert state.tests_passed is True

    def test_deployment_phase_transition(self):
        """State transitions correctly through deployment phase."""
        state = DevWorkflowState()
        state.log_phase("deploy_start")
        state.deployment_output = "PR #42 created"
        state.deploy_succeeded = True
        state.log_phase("deploy_end")
        assert "deploy_start" in state.timestamps
        assert "deploy_end" in state.timestamps
        assert state.deploy_succeeded is True

    def test_escalation_transition(self):
        """State records escalation when max retries reached."""
        state = DevWorkflowState()
        state.log_phase("escalated")
        state.errors.append("Max retries exhausted")
        assert "escalated" in state.timestamps
        assert len(state.errors) == 1

    def test_full_happy_path_state(self):
        """Complete happy path state progression."""
        state = DevWorkflowState(
            feature_request="Add user authentication",
            project_path="/app",
            execution_id="exec-123",
        )
        state.log_phase("research_start")
        state.research_findings = "Found OAuth2 docs"
        state.log_phase("research_end")
        state.log_phase("planning_start")
        state.implementation_plan = "Use JWT tokens"
        state.log_phase("planning_end")
        state.log_phase("execution_start_attempt_1")
        state.code_summary = "Created auth.py"
        state.log_phase("execution_end_attempt_1")
        state.log_phase("review_start_attempt_1")
        state.review_passed = True
        state.review_feedback = "LGTM"
        state.log_phase("review_end_attempt_1")
        state.log_phase("testing_start_attempt_1")
        state.tests_passed = True
        state.test_results = "10/10 passing"
        state.log_phase("testing_end_attempt_1")
        state.log_phase("deploy_start")
        state.deploy_succeeded = True
        state.deployment_output = "PR #42"
        state.log_phase("deploy_end")
        assert state.review_passed
        assert state.tests_passed
        assert state.deploy_succeeded
        assert len(state.errors) == 0

    def test_retry_loop_state(self):
        """State correctly tracks retry loop behavior."""
        state = DevWorkflowState()
        for i in range(1, 4):
            state.log_phase(f"execution_start_attempt_{i}")
            state.log_phase(f"execution_end_attempt_{i}")
            state.log_phase(f"review_start_attempt_{i}")
            if i < 3:
                state.review_passed = False
                state.review_feedback = f"Attempt {i} failed"
                state.errors.append(f"Review attempt {i} failed")
            else:
                state.review_passed = True
            state.log_phase(f"review_end_attempt_{i}")
        assert state.retry_count == 0
        assert state.review_passed is True
        assert len(state.errors) == 2
