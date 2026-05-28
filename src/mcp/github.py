import asyncio
import os
import json
import requests
from typing import Dict, Any, Optional, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client
from src.config import Config

# Step-by-step instructions for setting up the GitHub MCP server:
# 1. Ensure Node.js (version 18+) is installed.
# 2. Set GITHUB_PERSONAL_ACCESS_TOKEN in your environment.
#    Since we require read-only access, only check 'repo' scope with read-only permission.
# 3. Spawn server using `npx -y @modelcontextprotocol/server-github`.

async def get_repo_structure_async() -> str:
    """
    Connects to the GitHub MCP server to crawl/list repository structure,
    or falls back to local file system scanning if token is missing.
    """
    token = Config.GITHUB_TOKEN or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    owner = Config.GITHUB_OWNER or os.getenv("GITHUB_OWNER")
    repo = Config.GITHUB_REPO or os.getenv("GITHUB_REPO")

    if not token or not owner or not repo:
        # Fallback to local workspace scanning if Github env is not fully configured
        # This allows offline development / testing of the orchestrator.
        return _get_local_repo_structure()

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": token}
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Use MCP tools to find codebase details
                # The server-github tool commonly has search_code or get_file_contents.
                # Since we want structure, we will use a git tree API or fallback to REST API
                # for retrieving the repository tree structure.
                url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
                headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    tree_data = response.json()
                    paths = [item.get("path") for item in tree_data.get("tree", [])]
                    # Filter out .git, node_modules, etc. to save tokens
                    clean_paths = [p for p in paths if not p.startswith((".git/", "node_modules/", "__pycache__/"))]
                    return "\n".join(clean_paths)
                else:
                    return f"Error fetching tree structure via GitHub API: {response.text}"
    except Exception as e:
        return f"Failed to execute GitHub MCP client operation: {str(e)}. Falling back to local structure:\n{_get_local_repo_structure()}"

def _get_local_repo_structure() -> str:
    """
    Fallback method to fetch local codebase structure recursively.
    """
    # Use current working directory d:/AI-AgentProject
    cwd = "d:/AI-AgentProject"
    structure = []
    for root, dirs, files in os.walk(cwd):
        # Modify dirs in-place to skip hidden and dependency folders
        dirs[:] = [d for d in dirs if not d.startswith(('.', '__pycache__', 'node_modules'))]
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), cwd)
            # Use forward slashes
            structure.append(rel_path.replace("\\", "/"))
    return "\n".join(structure)

async def get_pr_diff_async(pr_id: int) -> str:
    """
    Connects to GitHub to fetch the unified diff of a specific Pull Request.
    Enforces read-only schema headers to pull content securely.
    """
    token = Config.GITHUB_TOKEN or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    owner = Config.GITHUB_OWNER or os.getenv("GITHUB_OWNER")
    repo = Config.GITHUB_REPO or os.getenv("GITHUB_REPO")

    if not token or not owner or not repo:
        return "Error: GitHub credentials or target repository settings are missing."

    # Using the standard Accept: application/vnd.github.v3.diff header, 
    # GitHub directly returns a formatted, clean unified diff string instead of JSON.
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    try:
        # Run in executor to avoid blocking the async event loop
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: requests.get(url, headers=headers)
        )
        
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching PR diff (Status {response.status_code}): {response.text}"
    except Exception as e:
        return f"Failed to retrieve PR diff due to an exception: {str(e)}"

# Synchronous wrappers
def get_repo_structure() -> str:
    try:
        return asyncio.run(get_repo_structure_async())
    except Exception as e:
        return f"Error scanning repository structure: {str(e)}"

def get_pr_diff(pr_id: int) -> str:
    try:
        return asyncio.run(get_pr_diff_async(pr_id))
    except Exception as e:
        return f"Error retrieving PR diff: {str(e)}"
