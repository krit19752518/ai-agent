from src.workflow import app, AgentState

# Create mock state with sample logs
sample_logs = """[INFO] Starting build\n[ERROR] Something failed\nTraceback (most recent call last):\n  File \"app.py\", line 10, in <module>\n    raise Exception(\"boom\")\nException: boom\n[INFO] Build finished"""

state = AgentState(
    jira_ticket_id='ANTG-101',
    raw_requirement='Test requirement for devops analysis',
    raw_logs=sample_logs
)

# Run the compiled workflow
result = app.invoke(state)

print('Final state keys:', list(result.keys()))
print('devops_analysis snippet:', result.get('devops_analysis', '')[:200])
print('downstream_report present?', 'downstream_report' in result)
