# test
"""
Dev Workflow Flow
=================
Researcher → Planner → [Executor ⇄ Reviewer]* → [Tester → Executor ⇄ Reviewer]* → Deployer

Architecture decision:
  - Main phase transitions (research → plan → pipeline → deploy) use CrewAI events.
  - Retry loops are imperative Python (while) inside two methods:
      · execution_and_review_loop  — executor + reviewer retries
      · testing_and_fix_loop       — tester + optional executor/reviewer fix cycles
  This avoids the async cycle problem in CrewAI's event engine (which was designed
  for DAGs, not cyclic graphs). The event-driven structure is preserved for the
  high-level pipeline; retries are handled safely in Python.
"""

import json
import re
from pathlib import Path
from typing import Optional

from crewai.flow.flow import Flow, start, listen, router
from dev_workflow.state import DevWorkflowState
from dev_workflow import emitter as _emit
from dev_workflow.crews import (
    ResearcherCrew,
    PlannerCrew,
    ExecutorCrew,
    ReviewerCrew,
    TesterCrew,
    DeployerCrew,
)

_D = "=" * 60


class FileWriter:
    """Handles file creation from executor output."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_file(self, file_path: str, content: str) -> bool:
        """Write a single file to disk."""
        try:
            dest = self.base_path / file_path.strip()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content.strip())
            print(f"  ✓ Wrote file: {file_path}")
            return True
        except OSError as e:
            print(f"  ⚠️  Write error for {file_path}: {e}")
            return False

    def parse_and_write(self, text: str) -> int:
        """Parse executor output and write all discovered files. Returns count of files written."""
        written = 0
        written += self._parse_json_blocks(text)
        written += self._parse_file_blocks(text)
        written += self._parse_code_blocks(text)
        written += self._parse_plain_file_references(text)
        return written

    def _parse_json_blocks(self, text: str) -> int:
        """Parse JSON blocks with file/content structure."""
        written = 0
        pattern = r"```json\s*\n(\{.*?\})\n```"
        for match in re.finditer(pattern, text, re.DOTALL):
            try:
                obj = json.loads(match.group(1))
                file_path = obj.get("file", "")
                content = obj.get("content", "")
                if file_path and content:
                    if self.write_file(file_path, content):
                        written += 1
            except (json.JSONDecodeError, OSError) as e:
                print(f"  ⚠️  JSON parse error: {e}")
        return written

    def _parse_file_blocks(self, text: str) -> int:
        """Parse ```file:path blocks."""
        written = 0
        pattern = r"```file:([^\n]+)\n(.*?)```"
        for match in re.finditer(pattern, text, re.DOTALL):
            file_path = match.group(1).strip()
            content = match.group(2)
            if self.write_file(file_path, content):
                written += 1
        return written

    def _parse_code_blocks(self, text: str) -> int:
        """Parse code blocks with file path hints."""
        written = 0
        code_extensions = {
            "py", "js", "ts", "tsx", "jsx", "go", "java",
            "rs", "c", "cpp", "h", "cs", "rb", "php", "swift"
        }
        pattern = r"```(\w+)?\s*\n(.*?)```"
        for match in re.finditer(pattern, text, re.DOTALL):
            lang = match.group(1) or ""
            content = match.group(2).strip()
            if lang.lower() in code_extensions:
                file_path = self._extract_file_path(content, lang)
                if file_path and self.write_file(file_path, content):
                    written += 1
        return written

    def _extract_file_path(self, content: str, lang: str) -> Optional[str]:
        """Extract file path from code block content."""
        if "\n" not in content:
            return None
        first_line = content.split("\n")[0].strip()
        patterns = [
            rf"^#\s*file:\s*(.+\.{lang})$",
            rf"^//\s*file:\s*(.+\.{lang})$",
            rf"^/\*\s*file:\s*(.+\.{lang})$",
            rf"^#\s*path:\s*(.+)$",
            rf"^//\s*path:\s*(.+)$",
            r"^(\S+\.\w+)$",
        ]
        for pat in patterns:
            m = re.match(pat, first_line, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _parse_plain_file_references(self, text: str) -> int:
        """Parse explicit file path references in text."""
        written = 0
        patterns = [
            r'(?:created|written|new file)[:\s]+[`"]?([^\s`"\']+\.(?:py|js|ts|tsx|jsx|go|java|rs|c|cpp|h|cs|rb|php|swift))[`"]?',
            r'file[:\s]+[`"]?([^\s`"\']+\.(?:py|js|ts|tsx|jsx|go|java|rs|c|cpp|h|cs|rb|php|swift))[`"]?[:\s]+is[:\s]+',
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                file_path = m.group(1).strip()
                if file_path and self._find_content_for_path(text, file_path):
                    content = self._find_content_for_path(text, file_path)
                    if content and self.write_file(file_path, content):
                        written += 1
        return written

    def _find_content_for_path(self, text: str, file_path: str) -> Optional[str]:
        """Find code content associated with a file path in text."""
        escaped = re.escape(file_path)
        pattern = rf"{escaped}[^\n]*\n(```\w*\n.*?\n```)"
        m = re.search(pattern, text, re.DOTALL)
        if m:
            inner = m.group(1)
            code_m = re.search(r"```\w*\n(.*?)\n```", inner, re.DOTALL)
            if code_m:
                return code_m.group(1)
        return None


class DevWorkflowFlow(Flow[DevWorkflowState]):
    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 1 — Research
    # ─────────────────────────────────────────────────────────────────────────

    @start()
    def research_phase(self):
        print(f"\n{_D}\n🔍 PHASE 1: Research\n{_D}")
        self.state.log_phase("research_start")
        _emit.emit(
            self.state.execution_id,
            "phase_started",
            "research",
            "Starting research phase",
        )
        _crew = ResearcherCrew()
        _crew.execution_id = self.state.execution_id
        result = _crew.crew().kickoff(
            inputs={
                "feature_request": self.state.feature_request,
                "project_path": self.state.project_path,
            }
        )
        self.state.research_findings = result.raw
        self.state.log_phase("research_end")
        _emit.emit(
            self.state.execution_id, "phase_completed", "research", "Research complete"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 2 — Planning
    # ─────────────────────────────────────────────────────────────────────────

    @listen(research_phase)
    def planning_phase(self):
        print(f"\n{_D}\n📋 PHASE 2: Planning\n{_D}")
        self.state.log_phase("planning_start")
        _emit.emit(
            self.state.execution_id,
            "phase_started",
            "planning",
            "Creating implementation plan",
        )
        _crew = PlannerCrew()
        _crew.execution_id = self.state.execution_id
        result = _crew.crew().kickoff(
            inputs={
                "feature_request": self.state.feature_request,
                "research_findings": self.state.research_findings,
                "project_path": self.state.project_path,
            }
        )
        self.state.implementation_plan = result.raw
        self.state.log_phase("planning_end")
        _emit.emit(self.state.execution_id, "phase_completed", "planning", "Plan ready")

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 3+4 — Execution + Review loop
    # Imperative while loop: avoids async cycle issues in CrewAI's event engine.
    # ─────────────────────────────────────────────────────────────────────────

    @listen(planning_phase)
    def execution_and_review_loop(self):
        while True:
            if self._is_cancelled():
                self.state.review_passed = True
                return
            self._run_executor()
            self._run_reviewer()

            if self.state.review_passed:
                return  # @router will send to "do_test"

            if self.state.retry_count >= self.state.max_retries:
                self.state.errors.append(
                    f"Review failed after {self.state.retry_count} attempts. "
                    f"Last feedback: {self.state.review_feedback}"
                )
                self.state.log_phase("escalated")
                return  # @router will send to "escalate"

    @router(execution_and_review_loop)
    def route_after_review(self):
        if not self.state.review_passed:
            return "escalate"
        return "do_test"

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 5 — Testing + fix loop
    # When tests fail: re-execute → re-review (must pass) → re-test.
    # ─────────────────────────────────────────────────────────────────────────

    @listen("do_test")
    def testing_and_fix_loop(self):
        while True:
            if self._is_cancelled():
                self.state.tests_passed = True
                return
            self._run_tester()

            if self.state.tests_passed:
                return  # @router will send to "do_deploy"

            if self.state.test_retry_count >= self.state.max_test_retries:
                self.state.errors.append(
                    f"Tests failed after {self.state.test_retry_count} attempts. "
                    f"Failures: {self.state.test_results}"
                )
                self.state.log_phase("escalated")
                return  # @router will send to "escalate"

            # Fix for test failures: re-run executor and reviewer before re-testing
            self.state.review_feedback = ""
            while True:
                self._run_executor()
                self._run_reviewer()

                if self.state.review_passed:
                    break  # inner loop OK → outer loop will re-run tests

                if self.state.retry_count >= self.state.max_retries:
                    self.state.errors.append(
                        f"Review escalation during test fix after "
                        f"{self.state.retry_count} attempts."
                    )
                    self.state.log_phase("escalated")
                    return  # @router will send to "escalate"

    @router(testing_and_fix_loop)
    def route_after_tests(self):
        if not self.state.tests_passed:
            return "escalate"
        return "do_deploy"

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 6 — Deployment
    # ─────────────────────────────────────────────────────────────────────────

    @listen("do_deploy")
    def deployment_phase(self):
        print(f"\n{_D}\n🚀 PHASE 6: Deployment\n{_D}")
        self.state.log_phase("deploy_start")
        _emit.emit(self.state.execution_id, "phase_started", "deployment", "Deploying")
        _crew = DeployerCrew()
        _crew.execution_id = self.state.execution_id
        result = _crew.crew().kickoff(
            inputs={
                "feature_request": self.state.feature_request,
                "project_path": self.state.project_path,
            }
        )
        self.state.deployment_output = result.raw
        self.state.deploy_succeeded = True
        self.state.log_phase("deploy_end")
        _emit.emit(
            self.state.execution_id,
            "phase_completed",
            "deployment",
            "Deployment successful",
        )
        print(f"\n✅ WORKFLOW COMPLETE — Deployment successful!")

    # ─────────────────────────────────────────────────────────────────────────
    # ESCALATION — max retries exhausted
    # ─────────────────────────────────────────────────────────────────────────

    @listen("escalate")
    def escalate(self):
        print(f"\n{_D}\n⚠️  ESCALATION: Max retries exhausted\n{_D}")
        for err in self.state.errors:
            print(f"  ERROR: {err}")
        print(f"\n  Last review feedback : {self.state.review_feedback}")
        print(f"  Last test results    : {self.state.test_results}")

        _emit.emit(
            self.state.execution_id,
            "execution_escalated",
            "",
            "Max retries exhausted — human intervention required",
            {"errors": self.state.errors},
        )

        self.state.review_passed = True

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers (not Flow methods — no decorators)
    # ─────────────────────────────────────────────────────────────────────────

    def _run_executor(self):
        self.state.retry_count += 1
        label = f"{self.state.retry_count}/{self.state.max_retries}"
        print(f"\n{_D}\n💻 PHASE 3: Execution (attempt {label})\n{_D}")
        if self.state.retry_count > 1:
            print(f"  ♻️  Review feedback : {self.state.review_feedback or 'none'}")
            print(f"  ♻️  Test failures   : {self.state.test_results or 'none'}")
        self.state.log_phase(f"execution_start_attempt_{self.state.retry_count}")
        _emit.emit(
            self.state.execution_id,
            "phase_started",
            "execution",
            f"Execution attempt {self.state.retry_count}/{self.state.max_retries}",
            {
                "retry_count": self.state.retry_count,
                "reviewer_feedback": self.state.review_feedback,
                "tester_feedback": self.state.test_results,
            },
        )
        _crew = ExecutorCrew()
        _crew.execution_id = self.state.execution_id
        result = _crew.crew().kickoff(
            inputs={
                "feature_request": self.state.feature_request,
                "implementation_plan": self.state.implementation_plan,
                "project_path": self.state.project_path,
                "reviewer_feedback": self.state.review_feedback
                or "None — first implementation.",
                "tester_feedback": self.state.test_results
                or "None — first implementation.",
            }
        )
        self.state.code_summary = result.raw

        if not self._validate_executor_output():
            self.state.review_passed = False
            self.state.review_feedback = (
                "Executor did not create any code files. "
                "Please use FileWriterTool to create actual files."
            )
            return

        self.state.log_phase(f"execution_end_attempt_{self.state.retry_count}")
        _emit.emit(
            self.state.execution_id,
            "phase_completed",
            "execution",
            "Code written successfully",
        )

    def _run_reviewer(self):
        print(
            f"\n{_D}\n🔎 PHASE 4: Code Review (attempt {self.state.retry_count})\n{_D}"
        )
        self.state.log_phase(f"review_start_attempt_{self.state.retry_count}")
        _emit.emit(
            self.state.execution_id,
            "phase_started",
            "review",
            f"Code review attempt {self.state.retry_count}",
        )
        _crew = ReviewerCrew()
        _crew.execution_id = self.state.execution_id
        result = _crew.crew().kickoff(
            inputs={
                "feature_request": self.state.feature_request,
                "implementation_plan": self.state.implementation_plan,
                "project_path": self.state.project_path,
            }
        )
        review = self._parse_review(result.raw)
        self.state.review_passed = review["passed"]
        self.state.review_feedback = review["feedback"]
        status = (
            "✅ PASSED"
            if review["passed"]
            else f"❌ FAILED (severity: {review['severity']})"
        )
        print(f"\n  Review: {status}")
        self.state.log_phase(f"review_end_attempt_{self.state.retry_count}")
        _emit.emit(
            self.state.execution_id,
            "phase_completed" if review["passed"] else "phase_failed",
            "review",
            f"Review {'passed' if review['passed'] else 'failed'}: {review['feedback'][:120]}",
            {
                "passed": review["passed"],
                "severity": review["severity"],
                "issues": review["issues"],
            },
        )

    def _parse_and_write_files(self, text: str) -> int:
        """Parse executor output text and write discovered file creations to disk."""
        writer = FileWriter(Path(self.state.project_path))
        return writer.parse_and_write(text)

    def _validate_executor_output(self) -> bool:
        """Check that executor actually created files in project_path."""
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".go",
            ".java",
            ".rs",
            ".c",
            ".cpp",
            ".h",
        }
        project_path = Path(self.state.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        written = self._parse_and_write_files(self.state.code_summary)
        if written > 0:
            print(f"  ✓ Flow wrote {written} files from executor output")

        code_files = [
            f
            for f in project_path.rglob("*")
            if f.is_file() and f.suffix in code_extensions
        ]
        if not code_files:
            print(f"⚠️  WARNING: No code files found in {project_path} after execution")
            return False
        print(f"✓ Found {len(code_files)} code files in {project_path}")
        return True

    def _is_cancelled(self) -> bool:
        """Check if execution was cancelled or interrupted (e.g. server shutdown)."""
        from dev_workflow.api import store

        ex = store.get(self.state.execution_id)
        if ex and ex.get("status") in ("cancelled", "interrupted"):
            return True
        return False

    def _run_tester(self):
        self.state.test_retry_count += 1
        label = f"{self.state.test_retry_count}/{self.state.max_test_retries}"
        print(f"\n{_D}\n🧪 PHASE 5: Testing (attempt {label})\n{_D}")
        self.state.log_phase(f"testing_start_attempt_{self.state.test_retry_count}")
        _emit.emit(
            self.state.execution_id,
            "phase_started",
            "testing",
            f"Test run {self.state.test_retry_count}/{self.state.max_test_retries}",
        )
        _crew = TesterCrew()
        _crew.execution_id = self.state.execution_id
        result = _crew.crew().kickoff(
            inputs={
                "feature_request": self.state.feature_request,
                "project_path": self.state.project_path,
            }
        )
        tests = self._parse_tests(result.raw)
        self.state.tests_passed = tests["passed"]
        self.state.test_results = tests["feedback"]
        status = "✅ PASSED" if tests["passed"] else "❌ FAILED"
        print(
            f"\n  Tests: {status} — {tests['total_tests']} total, "
            f"{tests['failed_tests']} failed, {tests['coverage']:.1f}% coverage"
        )
        self.state.log_phase(f"testing_end_attempt_{self.state.test_retry_count}")
        _emit.emit(
            self.state.execution_id,
            "phase_completed" if tests["passed"] else "phase_failed",
            "testing",
            f"Tests {'passed' if tests['passed'] else 'failed'}: {tests['total_tests']} total, {tests['failed_tests']} failed",
            {
                "passed": tests["passed"],
                "total": tests["total_tests"],
                "failed": tests["failed_tests"],
                "coverage": tests["coverage"],
            },
        )

    # ── JSON parsers (fallback-safe) ──────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Extract first JSON object from text (handles markdown code blocks)."""
        # Strip markdown fences
        text = re.sub(r"```(?:json)?\s*", "", text).strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}

    @staticmethod
    def _is_tool_call_json(text: str) -> bool:
        """Detect if text is a tool call JSON (has 'tool' and 'args' keys)."""
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return False
        try:
            obj = json.loads(match.group())
            return "tool" in obj and "args" in obj
        except json.JSONDecodeError:
            return False

    def _parse_review(self, raw: str) -> dict:
        if self._is_tool_call_json(raw):
            return {
                "passed": False,
                "severity": "critical",
                "issues": ["Reviewer returned tool call JSON instead of ReviewOutput"],
                "feedback": f"Malformed review output: reviewer did not produce valid JSON. Got: {raw[:200]}",
            }
        data = self._extract_json(raw)
        return {
            "passed": bool(data.get("passed", False)),
            "severity": str(data.get("severity", "unknown")),
            "issues": list(data.get("issues", [])),
            "feedback": str(data.get("feedback", raw[:500])),
        }

    def _parse_tests(self, raw: str) -> dict:
        data = self._extract_json(raw)
        return {
            "passed": bool(data.get("passed", False)),
            "total_tests": int(data.get("total_tests", 0)),
            "failed_tests": int(data.get("failed_tests", 0)),
            "failures": list(data.get("failures", [])),
            "coverage": float(data.get("coverage", 0.0)),
            "feedback": str(data.get("feedback", raw[:500])),
        }
