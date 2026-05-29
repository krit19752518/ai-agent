import pytest
from src.workflow import app, AgentState

# Sample CI log containing an error and traceback
def get_sample_logs():
    return """[INFO] Starting build\n[ERROR] Something failed\nTraceback (most recent call last):\n  File \"app.py\", line 10, in <module>\n    raise Exception(\"boom\")\nException: boom\n[INFO] Build finished"""

@pytest.fixture
def mock_state():
    return AgentState(
        jira_ticket_id="ANTG-101",
        raw_requirement="Test requirement for devops analysis",
        raw_logs=get_sample_logs(),
    )

def test_devops_analysis_contains_thai_headings(mock_state):
    result = app.invoke(mock_state, {"configurable": {"thread_id": "test_thread"}})
    # The DevOps Agent should produce Thai headings "## ❌ สาเหตุที่พัง"
    devops_output = result.get("devops_analysis", "")
    assert "## ❌ สาเหตุที่พัง" in devops_output, "DevOps analysis missing Thai heading"
    assert "## 🛠️ วิธีแก้ไขที่แนะนำ" in devops_output, "DevOps analysis missing recommendation heading"

def test_downstream_report_is_present(mock_state):
    result = app.invoke(mock_state, {"configurable": {"thread_id": "test_thread"}})
    assert "downstream_report" in result, "Downstream review node did not produce a report"
    # Ensure the downstream report includes both QA and DevOps sections
    downstream = result["downstream_report"]
    assert "## 📊 Downstream Review Summary" in downstream
    assert "## 📋 QA Test Matrix" in downstream
    assert "## ❌ สาเหตุที่พัง" in downstream

