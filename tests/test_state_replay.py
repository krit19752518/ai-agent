import pytest
from src.core.state import AgentState

def test_agent_state_pydantic_validation():
    state = AgentState(
        jira_ticket_id="ANTG-101",
        raw_requirement="Test requirement",
        recorded_steps=[{"event": "click", "selector": "#btn"}]
    )
    assert state.jira_ticket_id == "ANTG-101"
    assert state.raw_requirement == "Test requirement"
    assert len(state.recorded_steps) == 1
    assert state.recorded_steps[0]["event"] == "click"

def test_agent_state_default_values():
    state = AgentState()
    assert state.playwright_retry_count == 0
    assert state.playwright_script == ""
    assert state.playwright_logs == ""
    assert state.recorded_steps == []
    assert state.dom_snapshots == []
