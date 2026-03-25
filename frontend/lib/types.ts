export type PhaseId = "research" | "planning" | "execution" | "review" | "testing" | "deployment";
export type Status = "pending" | "running" | "completed" | "failed" | "escalated" | "cancelled" | "interrupted";

export interface PhaseStatus {
  name: PhaseId;
  label: string;
  status: Status;
  started_at: string | null;
  completed_at: string | null;
  output: string | null;
}

export interface TokenUsage {
  total_tokens?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  estimated_cost_usd?: number;
}

export interface Execution {
  id: string;
  feature_request: string;
  project_path: string;
  status: Status;
  current_phase: PhaseId | null;
  current_agent: string | null;
  phases: PhaseStatus[];
  retry_count: number;
  max_retries: number;
  test_retry_count: number;
  max_test_retries: number;
  errors: string[];
  log: WorkflowEvent[];
  token_usage: TokenUsage;
  cancelled_at: string | null;
  github_pr_url: string | null;
  github_branch: string | null;
  linear_issue_id: string | null;
  linear_issue_url: string | null;
  workspace_mode: string;
  github_repo: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface WorkflowEvent {
  execution_id: string;
  type: string;
  phase: PhaseId | "";
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}
