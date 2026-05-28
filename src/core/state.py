from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    """
    State definition for the Antigravity Agentic SDLC LangGraph orchestrator.
    Manages central state variables, tool responses, and approval flags.
    """
    # Core State Variables
    linear_issue_id: str             # The active ticket ID from Linear
    current_api_spec: Optional[str]  # OpenAPI or API specification YAML/JSON
    risk_score: float                # Overall risk calculation score (0.0 to 100.0)
    approval_status: str             # Decision gate status: 'PENDING', 'APPROVED', 'REJECTED'

    # Read-Only Fetched Contexts
    issue_details: Optional[str]     # Clean Markdown format of issue contents
    repo_structure: Optional[str]    # Codebase directory layout
    pr_diff: Optional[str]           # Unified diff from GitHub PR
    db_schema: Optional[str]         # Postgres Database Schema metadata map

    # Shared Context / Execution Log
    logs: List[Dict[str, Any]]        # Audit trail of agent decisions and state changes
