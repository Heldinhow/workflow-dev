"""Tests for all 6 crews — researcher, planner, executor, reviewer, tester, deployer."""

from unittest.mock import MagicMock, patch


class TestResearcherCrew:
    """Tests for ResearcherCrew."""

    def test_researcher_crew_has_execution_id(self):
        """ResearcherCrew has execution_id attribute."""
        from dev_workflow.crews.researcher.crew import ResearcherCrew
        crew = ResearcherCrew()
        assert hasattr(crew, "execution_id")
        crew.execution_id = "test-123"
        assert crew.execution_id == "test-123"

    def test_researcher_crew_has_crew_method(self):
        """ResearcherCrew has crew() method that returns a Crew."""
        from dev_workflow.crews.researcher.crew import ResearcherCrew
        crew = ResearcherCrew()
        with patch.object(crew, "agents", []), patch.object(crew, "tasks", []):
            result = crew.crew()
            assert result is not None

    def test_researcher_crew_has_researcher_agent(self):
        """ResearcherCrew has researcher agent."""
        from dev_workflow.crews.researcher.crew import ResearcherCrew
        crew = ResearcherCrew()
        with patch("dev_workflow.crews.researcher.crew.LLM"):
            agent = crew.researcher()
            assert agent is not None

    def test_researcher_crew_has_research_task(self):
        """ResearcherCrew has research_task."""
        from dev_workflow.crews.researcher.crew import ResearcherCrew
        crew = ResearcherCrew()
        with patch("dev_workflow.crews.researcher.crew.LLM"):
            task = crew.research_task()
            assert task is not None


class TestPlannerCrew:
    """Tests for PlannerCrew."""

    def test_planner_crew_has_execution_id(self):
        """PlannerCrew has execution_id attribute."""
        from dev_workflow.crews.planner.crew import PlannerCrew
        crew = PlannerCrew()
        assert hasattr(crew, "execution_id")
        crew.execution_id = "test-456"
        assert crew.execution_id == "test-456"

    def test_planner_crew_has_crew_method(self):
        """PlannerCrew has crew() method that returns a Crew."""
        from dev_workflow.crews.planner.crew import PlannerCrew
        crew = PlannerCrew()
        with patch.object(crew, "agents", []), patch.object(crew, "tasks", []):
            result = crew.crew()
            assert result is not None

    def test_planner_crew_has_planner_agent(self):
        """PlannerCrew has planner agent."""
        from dev_workflow.crews.planner.crew import PlannerCrew
        crew = PlannerCrew()
        with patch("dev_workflow.crews.planner.crew.LLM"):
            agent = crew.planner()
            assert agent is not None

    def test_planner_crew_has_plan_task(self):
        """PlannerCrew has plan_task."""
        from dev_workflow.crews.planner.crew import PlannerCrew
        crew = PlannerCrew()
        with patch("dev_workflow.crews.planner.crew.LLM"):
            task = crew.plan_task()
            assert task is not None


class TestExecutorCrew:
    """Tests for ExecutorCrew."""

    def test_executor_crew_has_execution_id(self):
        """ExecutorCrew has execution_id attribute."""
        from dev_workflow.crews.executor.crew import ExecutorCrew
        crew = ExecutorCrew()
        assert hasattr(crew, "execution_id")
        crew.execution_id = "test-789"
        assert crew.execution_id == "test-789"

    def test_executor_crew_has_crew_method(self):
        """ExecutorCrew has crew() method that returns a Crew."""
        from dev_workflow.crews.executor.crew import ExecutorCrew
        crew = ExecutorCrew()
        with patch.object(crew, "agents", []), patch.object(crew, "tasks", []):
            result = crew.crew()
            assert result is not None

    def test_executor_crew_has_executor_agent(self):
        """ExecutorCrew has executor agent."""
        from dev_workflow.crews.executor.crew import ExecutorCrew
        crew = ExecutorCrew()
        with patch("dev_workflow.crews.executor.crew.LLM"):
            agent = crew.executor()
            assert agent is not None

    def test_executor_crew_has_coding_task(self):
        """ExecutorCrew has coding_task."""
        from dev_workflow.crews.executor.crew import ExecutorCrew
        crew = ExecutorCrew()
        with patch("dev_workflow.crews.executor.crew.LLM"):
            task = crew.coding_task()
            assert task is not None

    def test_executor_crew_update_token_usage(self):
        """ExecutorCrew _update_token_usage handles token data correctly."""
        from dev_workflow.crews.executor.crew import ExecutorCrew
        crew = ExecutorCrew()
        crew.execution_id = "test-token"
        with patch("dev_workflow.crews.executor.crew.store") as mock_store:
            mock_store.get.return_value = {"token_usage": {}}
            crew._update_token_usage({
                "total_tokens": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50,
            })
            mock_store.update.assert_called_once()


class TestReviewerCrew:
    """Tests for ReviewerCrew."""

    def test_reviewer_crew_has_execution_id(self):
        """ReviewerCrew has execution_id attribute."""
        from dev_workflow.crews.reviewer.crew import ReviewerCrew
        crew = ReviewerCrew()
        assert hasattr(crew, "execution_id")
        crew.execution_id = "test-review"
        assert crew.execution_id == "test-review"

    def test_reviewer_crew_has_crew_method(self):
        """ReviewerCrew has crew() method that returns a Crew."""
        from dev_workflow.crews.reviewer.crew import ReviewerCrew
        crew = ReviewerCrew()
        with patch.object(crew, "agents", []), patch.object(crew, "tasks", []):
            result = crew.crew()
            assert result is not None

    def test_reviewer_crew_has_reviewer_agent(self):
        """ReviewerCrew has reviewer agent."""
        from dev_workflow.crews.reviewer.crew import ReviewerCrew
        crew = ReviewerCrew()
        with patch("dev_workflow.crews.reviewer.crew.LLM"):
            agent = crew.reviewer()
            assert agent is not None

    def test_reviewer_crew_has_review_task(self):
        """ReviewerCrew has review_task."""
        from dev_workflow.crews.reviewer.crew import ReviewerCrew
        crew = ReviewerCrew()
        with patch("dev_workflow.crews.reviewer.crew.LLM"):
            task = crew.review_task()
            assert task is not None

    def test_review_output_model(self):
        """ReviewOutput model validates correctly."""
        from dev_workflow.crews.reviewer.crew import ReviewOutput
        output = ReviewOutput(
            passed=True,
            severity="none",
            issues=[],
            feedback="LGTM",
        )
        assert output.passed is True
        assert output.severity == "none"
        assert output.issues == []
        assert output.feedback == "LGTM"

    def test_review_output_model_with_issues(self):
        """ReviewOutput model accepts issues list."""
        from dev_workflow.crews.reviewer.crew import ReviewOutput
        output = ReviewOutput(
            passed=False,
            severity="major",
            issues=["Missing error handling", "No tests"],
            feedback="Fix issues listed above.",
        )
        assert output.passed is False
        assert output.severity == "major"
        assert len(output.issues) == 2


class TestTesterCrew:
    """Tests for TesterCrew."""

    def test_tester_crew_has_execution_id(self):
        """TesterCrew has execution_id attribute."""
        from dev_workflow.crews.tester.crew import TesterCrew
        crew = TesterCrew()
        assert hasattr(crew, "execution_id")
        crew.execution_id = "test-test"
        assert crew.execution_id == "test-test"

    def test_tester_crew_has_crew_method(self):
        """TesterCrew has crew() method that returns a Crew."""
        from dev_workflow.crews.tester.crew import TesterCrew
        crew = TesterCrew()
        with patch.object(crew, "agents", []), patch.object(crew, "tasks", []):
            result = crew.crew()
            assert result is not None

    def test_tester_crew_has_tester_agent(self):
        """TesterCrew has tester agent."""
        from dev_workflow.crews.tester.crew import TesterCrew
        crew = TesterCrew()
        with patch("dev_workflow.crews.tester.crew.LLM"):
            agent = crew.tester()
            assert agent is not None

    def test_tester_crew_has_test_task(self):
        """TesterCrew has test_task."""
        from dev_workflow.crews.tester.crew import TesterCrew
        crew = TesterCrew()
        with patch("dev_workflow.crews.tester.crew.LLM"):
            task = crew.test_task()
            assert task is not None

    def test_test_output_model(self):
        """TestOutput model validates correctly."""
        from dev_workflow.crews.tester.crew import TestOutput
        output = TestOutput(
            passed=True,
            total_tests=10,
            failed_tests=0,
            failures=[],
            coverage=95.0,
            feedback="All tests passing.",
        )
        assert output.passed is True
        assert output.total_tests == 10
        assert output.failed_tests == 0
        assert output.coverage == 95.0

    def test_test_output_model_with_failures(self):
        """TestOutput model accepts failure details."""
        from dev_workflow.crews.tester.crew import TestOutput
        output = TestOutput(
            passed=False,
            total_tests=10,
            failed_tests=2,
            failures=["test_foo: AssertionError", "test_bar: KeyError"],
            coverage=55.0,
            feedback="Fix failing tests.",
        )
        assert output.passed is False
        assert output.failed_tests == 2
        assert len(output.failures) == 2


class TestDeployerCrew:
    """Tests for DeployerCrew."""

    def test_deployer_crew_has_execution_id(self):
        """DeployerCrew has execution_id attribute."""
        from dev_workflow.crews.deployer.crew import DeployerCrew
        crew = DeployerCrew()
        assert hasattr(crew, "execution_id")
        crew.execution_id = "test-deploy"
        assert crew.execution_id == "test-deploy"

    def test_deployer_crew_has_crew_method(self):
        """DeployerCrew has crew() method that returns a Crew."""
        from dev_workflow.crews.deployer.crew import DeployerCrew
        crew = DeployerCrew()
        with patch.object(crew, "agents", []), patch.object(crew, "tasks", []):
            result = crew.crew()
            assert result is not None

    def test_deployer_crew_has_deployer_agent(self):
        """DeployerCrew has deployer agent."""
        from dev_workflow.crews.deployer.crew import DeployerCrew
        crew = DeployerCrew()
        with patch("dev_workflow.crews.deployer.crew.LLM"):
            agent = crew.deployer()
            assert agent is not None

    def test_deployer_crew_has_deploy_task(self):
        """DeployerCrew has deploy_task."""
        from dev_workflow.crews.deployer.crew import DeployerCrew
        crew = DeployerCrew()
        with patch("dev_workflow.crews.deployer.crew.LLM"):
            task = crew.deploy_task()
            assert task is not None


class TestCrewImports:
    """Tests for crew module imports."""

    def test_all_crews_importable(self):
        """All 6 crews are importable from dev_workflow.crews."""
        from dev_workflow.crews import (
            ResearcherCrew,
            PlannerCrew,
            ExecutorCrew,
            ReviewerCrew,
            TesterCrew,
            DeployerCrew,
        )
        assert ResearcherCrew is not None
        assert PlannerCrew is not None
        assert ExecutorCrew is not None
        assert ReviewerCrew is not None
        assert TesterCrew is not None
        assert DeployerCrew is not None

    def test_crew_step_callback_handles_output(self):
        """Step callback handles various output formats."""
        from dev_workflow.crews.researcher.crew import ResearcherCrew
        crew = ResearcherCrew()
        crew.execution_id = "test-callback"
        with patch("dev_workflow.crews.researcher.crew._emit") as mock_emit:
            crew._step_callback(MagicMock(output="Test output"))
            mock_emit.emit.assert_called()
