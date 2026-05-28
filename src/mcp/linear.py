import asyncio
import os
import json
from typing import Dict, Any, Optional
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client
# นำเข้า TextContent มาเพื่อทำความสะอาด Type Hint และเคลียร์ปัญหา Linter
from mcp.types import TextContent
from src.config import Config

# Step-by-step instructions for setting up the Linear MCP server:
# 1. Ensure Node.js (version 18+) is installed.
# 2. Set LINEAR_API_KEY environment variable. Note: For this Phase 1 read-only requirement,
#    we recommend generating a Personal Access Token in Linear settings with Read-Only permissions.
# 3. Running `npx -y @linear/mcp-server` will start the server over stdin/stdout, which the client interacts with.

def parse_linear_issue(raw_issue: Dict[str, Any]) -> str:
    """
    Parses raw Linear issue JSON payload into a clean, human-readable Markdown format.
    Strips metadata noise to optimize Gemini context windows.
    """
    try:
        title = raw_issue.get("title", "No Title")
        identifier = raw_issue.get("identifier", "Unknown ID")
        description = raw_issue.get("description", "No description provided.")
        
        # State/Status parsing
        state_info = raw_issue.get("state", {})
        status = state_info.get("name", "Unknown Status") if isinstance(state_info, dict) else "Unknown Status"
        
        # Assignee parsing
        assignee_info = raw_issue.get("assignee", {})
        assignee = assignee_info.get("name", "Unassigned") if isinstance(assignee_info, dict) else "Unassigned"
        
        # Priority parsing
        priority = raw_issue.get("priorityLabel", "None")
        
        # Labels parsing
        labels_list = raw_issue.get("labels", {}).get("nodes", []) if isinstance(raw_issue.get("labels"), dict) else []
        labels = ", ".join([l.get("name", "") for l in labels_list if isinstance(l, dict)]) or "None"
        
        markdown_output = [
            f"# [{identifier}] {title}",
            f"- **Status**: {status}",
            f"- **Priority**: {priority}",
            f"- **Assignee**: {assignee}",
            f"- **Labels**: {labels}",
            "\n## Description",
            description,
        ]
        
        # Comments parsing if present
        comments_info = raw_issue.get("comments", {})
        if isinstance(comments_info, dict) and "nodes" in comments_info:
            comments = comments_info["nodes"]
            if comments:
                markdown_output.append("\n## Comments")
                for c in comments:
                    author = c.get("user", {}).get("name", "Anonymous")
                    body = c.get("body", "")
                    markdown_output.append(f"- **{author}**: {body}")

        return "\n".join(markdown_output)
    except Exception as e:
        # Fallback in case raw_issue is in an unexpected format
        return f"### Error parsing issue details: {str(e)}\nRaw Response:\n```json\n{json.dumps(raw_issue, indent=2)}\n```"

async def fetch_issue_details_async(issue_id: str) -> str:
    """
    Asynchronously spawns and connects to the `@linear/mcp-server` over stdio,
    queries the issue, and formats the output into clean Markdown.
    """
    api_key = Config.LINEAR_API_KEY or os.getenv("LINEAR_API_KEY")
    if not api_key:
        return f"Error: LINEAR_API_KEY environment variable is not set."

    # Setup connection parameters for the MCP server using npx
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@linear/mcp-server"],
        env={**os.environ, "LINEAR_API_KEY": api_key}
    )

    try:
        # Establish stdio connection with the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize protocol session
                await session.initialize()

                # Call the standard 'get_issue' tool provided by @linear/mcp-server
                result = await session.call_tool("get_issue", {"id": issue_id})
                
                # 1. แก้ไขให้เป็น .isError ตามสเปกของคลาสสแตนดาร์ดใน MCP SDK
                if result.isError:
                    return f"Error from Linear MCP: {result.content}"
                
                # 2. ทำการวนลูปแบบ Strict Type Guarding เพื่อคัดแยกเฉพาะ TextContent ออกมาอย่างปลอดภัย
                texts: list[str] = []
                if result.content:
                    for content in result.content:
                        if isinstance(content, TextContent):
                            # บังคับประกาศ Type เพื่อตบไหล่บอก Linter ว่านี่คือข้อความแน่นอน ห้ามฟ้อง Audio/Image อีก
                            text_item: TextContent = content
                            texts.append(text_item.text)
                
                # ประกอบข้อความ JSON ดิบที่ได้มาประมวลผลต่อ
                text_content = texts[0] if texts else "{}"
                raw_json = json.loads(text_content)
                
                return parse_linear_issue(raw_json)
    except Exception as e:
        return f"Failed to execute Linear MCP client operation: {str(e)}"

def fetch_issue_details(issue_id: str) -> str:
    """
    Synchronous wrapper for fetch_issue_details_async.
    """
    try:
        # Run async event loop
        return asyncio.run(fetch_issue_details_async(issue_id))
    except Exception as e:
        return f"Synchronous execution error: {str(e)}"