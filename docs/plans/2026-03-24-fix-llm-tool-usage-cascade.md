# Fix LLM Tool Usage Cascade (Issues #7, #8, #9, #10) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the cascade failure where the executor doesn't write code, reviewer returns malformed output, and escalation loops infinitely.

**Architecture:** The root cause is that the MiniMax LLM exits after a single tool call. This causes: no files written → reviewer gets empty output → returns tool call JSON → `_parse_review` fails → infinite escalation loop.

**Tech Stack:** Python, CrewAI, FastAPI, MiniMax LLM

**Root Cause Chain:**
```
#10: LLM exits after 1 tool call (MiniMax behavior)
  ↓
#7:  Executor has output_file that misleads + no validation
  ↓
#8:  Reviewer gets empty dir, returns tool call JSON
  ↓
#9:  escalate() doesn't emit terminal event → infinite loop
```

---

## Task 1: Fix executor task config — remove output_file, improve prompts

**Files:**
- Modify: `src/dev_workflow/crews/executor/config/tasks.yaml`
- Modify: `src/dev_workflow/crews/executor/config/agents.yaml`

**Step 1: Write failing test**

```python
# tests/test_executor_validation.py

def test_executor_task_has_no_output_file():
    """Executor task must NOT have output_file — it misleads the LLM."""
    import yaml
    with open("src/dev_workflow/crews/executor/config/tasks.yaml") as f:
        config = yaml.safe_load(f)
    task = config["coding_task"]
    assert "output_file" not in task, \
        "output_file causes CrewAI to write summary, not real code"

def test_executor_task_forces_file_writer_usage():
    """Task description must explicitly require FileWriterTool for ALL code."""
    import yaml
    with open("src/dev_workflow/crews/executor/config/tasks.yaml") as f:
        config = yaml.safe_load(f)
    desc = config["coding_task"]["description"]
    assert "FileWriterTool" in desc, \
        "Task must mention FileWriterTool explicitly"
    assert "must" in desc.lower() or "required" in desc.lower(), \
        "Task must use mandatory language"
```

**Step 2: Run tests — verify they fail**

Run: `pytest tests/test_executor_validation.py -v`
Expected: FAIL — output_file exists, FileWriterTool not mentioned

**Step 3: Update tasks.yaml — remove output_file, add explicit tool requirements**

```yaml
coding_task:
  description: >
    Implement the feature according to the plan.

    Feature: {feature_request}
    Implementation plan: {implementation_plan}
    Project path: {project_path}

    --- FEEDBACK TO FIX (if any) ---
    Code review feedback: {reviewer_feedback}
    Test failures: {tester_feedback}
    --------------------------------

    CRITICAL INSTRUCTIONS:
    1. You MUST use FileWriterTool to create every code file — do NOT skip any files
    2. First, read existing project files with DirectoryReadTool to understand structure
    3. Write ALL files listed in the implementation plan using FileWriterTool
    4. After writing files, use ShellTool to verify syntax (e.g., `python -m py_compile <file>`)
    5. Do NOT return until ALL files are created and verified
    6. Install dependencies using ShellTool BEFORE writing code that needs them
  expected_output: >
    A detailed summary listing every file created/modified with paths,
    and confirmation that all files pass syntax checks.
    IMPORTANT: You must actually create the files using FileWriterTool,
    not just describe what you would create.
```

**Step 4: Update agents.yaml — add tool usage emphasis**

```yaml
executor:
  role: Senior Software Engineer
  goal: >
    Implement clean, production-ready code strictly following the plan.
    You MUST use FileWriterTool to create actual files — do not skip file creation.
    When given feedback from reviewer or tester, fix ALL identified issues precisely.
  backstory: >
    You are a skilled software developer who writes clean, well-documented,
    tested code. You follow the implementation plan strictly, handle edge cases,
    and when given review or test feedback, you address every single issue
    with precision — never ignoring or partially fixing problems.
    IMPORTANT: You must physically create files using FileWriterTool.
    Reading files or describing code is NOT sufficient.
```

**Step 5: Run tests — verify they pass**

Run: `pytest tests/test_executor_validation.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/dev_workflow/crews/executor/config/tasks.yaml src/dev_workflow/crews/executor/config/agents.yaml tests/test_executor_validation.py
git commit -m "fix: remove output_file, force FileWriterTool usage in executor"
```

---

## Task 2: Add post-execution file validation in flow.py

**Files:**
- Modify: `src/dev_workflow/flow.py`
- Create: `tests/test_execution_validation.py`

**Step 1: Write failing test**

```python
# tests/test_execution_validation.py

def test_flow_validates_files_created_after_execution(tmp_path):
    """Flow must validate that executor created files, not just assume success."""
    from unittest.mock import MagicMock, patch
    from dev_workflow.flow import DevWorkflowFlow

    # Simulate executor that doesn't create files
    with patch("dev_workflow.flow.ExecutorCrew") as m_exec:
        mock_result = MagicMock()
        mock_result.raw = "Code written successfully"  # LLM lies!
        m_exec.return_value.crew.return_value.kickoff.return_value = mock_result
        
        with patch("dev_workflow.flow.ReviewerCrew") as m_rev:
            mock_review = MagicMock()
            mock_review.raw = '{"passed": true, "severity": "none", "issues": [], "feedback": "LGTM"}'
            m_rev.return_value.crew.return_value.kickoff.return_value = mock_review
            
            flow = DevWorkflowFlow()
            flow.state.project_path = str(tmp_path)
            flow.state.feature_request = "test feature"
            flow.state.implementation_plan = "create test.py"
            
            # The flow should detect no files were created
            flow.execution_and_review_loop()
            
            # Should have logged a warning about no files
            # or taken some recovery action
```

**Step 2: Run test — verify it fails**

Run: `pytest tests/test_execution_validation.py -v`
Expected: FAIL — no validation exists yet

**Step 3: Add validation in _run_executor**

In `flow.py`, add a helper method and call it after executor runs:

```python
def _validate_executor_output(self) -> bool:
    """Check that executor actually created files in project_path."""
    import os
    from pathlib import Path
    
    project_path = Path(self.state.project_path)
    
    # Check for common code file extensions
    code_files = list(project_path.rglob("*.py")) + \
                 list(project_path.rglob("*.js")) + \
                 list(project_path.rglob("*.ts")) + \
                 list(project_path.rglob("*.tsx")) + \
                 list(project_path.rglob("*.go")) + \
                 list(project_path.rglob("*.java"))
    
    if not code_files:
        warning = f"⚠️  WARNING: No code files found in {project_path} after execution"
        print(warning)
        self.state.errors.append(warning)
        return False
    return True
```

Then modify `_run_executor` to call this after kickoff:

```python
def _run_executor(self):
    # ... existing code ...
    result = _crew.crew().kickoff(inputs={...})
    self.state.code_summary = result.raw
    
    # ADD THIS: Validate files were actually created
    if not self._validate_executor_output():
        self.state.review_passed = False
        self.state.review_feedback = "Executor did not create any code files. Please use FileWriterTool to create actual files."
        return  # Skip to reviewer with failed state
    
    self.state.log_phase(f"execution_end_attempt_{self.state.retry_count}")
    _emit.emit(self.state.execution_id, "phase_completed", "execution", "Code written successfully")
```

**Step 4: Run tests — verify they pass**

Run: `pytest tests/test_execution_validation.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/dev_workflow/flow.py tests/test_execution_validation.py
git commit -m "fix: add post-execution file validation in flow"
```

---

## Task 3: Fix _parse_review to detect tool call JSON

**Files:**
- Modify: `src/dev_workflow/flow.py`
- Modify: `tests/test_flow.py`

**Step 1: Write failing test**

```python
# In tests/test_flow.py, add:

def test_parse_review_rejects_tool_call_json():
    """_parse_review must detect and reject tool call JSON format."""
    from dev_workflow.flow import DevWorkflowFlow
    
    flow = DevWorkflowFlow()
    
    # Tool call JSON that the reviewer incorrectly returns
    tool_call_json = '{"tool": "list_files_in_directory", "args": {"--directory": "./output"}}'
    result = flow._parse_review(tool_call_json)
    
    # Should NOT return passed=True for malformed output
    assert result["passed"] == False, \
        "Tool call JSON should be rejected"
    assert "malformed" in result["feedback"].lower() or "error" in result["feedback"].lower(), \
        "Should indicate parsing error"
```

**Step 2: Run test — verify it fails**

Run: `pytest tests/test_flow.py::test_parse_review_rejects_tool_call_json -v`
Expected: FAIL — current implementation returns passed=False but with raw text

**Step 3: Fix _parse_review**

```python
def _parse_review(self, raw: str) -> dict:
    # First, detect tool call JSON (malformed output from reviewer)
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

@staticmethod
def _is_tool_call_json(text: str) -> bool:
    """Detect if text is a tool call JSON (has 'tool' and 'args' keys)."""
    import json
    import re
    # Try to extract JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return False
    try:
        obj = json.loads(match.group())
        return "tool" in obj and "args" in obj
    except json.JSONDecodeError:
        return False
```

**Step 4: Run test — verify it passes**

Run: `pytest tests/test_flow.py::test_parse_review_rejects_tool_call_json -v`
Expected: PASS

**Step 5: Run all flow tests to ensure no regression**

Run: `pytest tests/test_flow.py -v`
Expected: All tests pass

**Step 6: Commit**

```bash
git add src/dev_workflow/flow.py tests/test_flow.py
git commit -m "fix: detect and reject tool call JSON in _parse_review"
```

---

## Task 4: Fix infinite escalation loop — escalate must emit terminal event

**Files:**
- Modify: `src/dev_workflow/flow.py`
- Modify: `tests/test_flow.py`

**Step 1: Write failing test**

```python
# In tests/test_flow.py, add:

@patch(f"{P}.ReviewerCrew")
@patch(f"{P}.ExecutorCrew")
def test_escalate_terminates_flow(m_exec, m_rev):
    """escalate() must emit execution_escalated event to terminate the flow."""
    from dev_workflow.flow import DevWorkflowFlow
    
    _setup(m_exec, raw="code")
    _setup(m_rev, side_effects=[
        _crew_result(pydantic=_review(passed=False, feedback="Critical bug"))
        for _ in range(10)
    ])
    
    flow = DevWorkflowFlow()
    flow.state.feature_request = "Broken feature"
    flow.state.implementation_plan = "plan"
    flow.state.project_path = "./output"
    
    # Track events emitted
    emitted_events = []
    original_emit = flow._emit.emit
    
    def track_emit(*args):
        emitted_events.append(args)
        return original_emit(*args)
    
    with patch.object(flow, '_emit') as mock_emit:
        mock_emit.emit = track_emit
        flow.execution_and_review_loop()
    
    # escalate should have been called and should have emitted execution_escalated
    escalate_events = [e for e in emitted_events if e[2] == "execution_escalated"]
    assert len(escalate_events) > 0, "escalate must emit execution_escalated event"
```

**Step 2: Run test — verify it fails**

Run: `pytest tests/test_flow.py::test_escalate_terminates_flow -v`
Expected: FAIL — execution_escalated not emitted

**Step 3: Fix escalate method**

```python
@listen("escalate")
def escalate(self):
    print(f"\n{_D}\n⚠️  ESCALATION: Max retries exhausted\n{_D}")
    for err in self.state.errors:
        print(f"  ERROR: {err}")
    print(f"\n  Last review feedback : {self.state.review_feedback}")
    print(f"  Last test results    : {self.state.test_results}")
    
    # Emit terminal event BEFORE returning — this signals CrewAI the flow is done
    _emit.emit(
        self.state.execution_id,
        "execution_escalated",
        "",
        "Max retries exhausted — human intervention required",
        {"errors": self.state.errors}
    )
```

**Step 4: Run test — verify it passes**

Run: `pytest tests/test_flow.py::test_escalate_terminates_flow -v`
Expected: PASS

**Step 5: Run all flow tests**

Run: `pytest tests/test_flow.py -v`
Expected: All tests pass

**Step 6: Commit**

```bash
git add src/dev_workflow/flow.py tests/test_flow.py
git commit -m "fix: escalate emits terminal event to prevent infinite loop"
```

---

## Task 5: Verify all tests pass

**Step 1: Run full test suite**

Run: `pytest tests/ -v`

**Step 2: If any failures, fix and re-run**

---

## Summary of Changes

| Issue | Fix |
|-------|-----|
| #10 | Task 1: Removed output_file, added explicit FileWriterTool instructions |
| #7 | Task 2: Added `_validate_executor_output()` to check files exist |
| #8 | Task 3: `_is_tool_call_json()` detects and rejects tool call format |
| #9 | Task 4: `escalate()` now emits `execution_escalated` terminal event |
