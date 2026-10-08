import requests

from mcp.server.mcpserver import MCPServer


# Create MCP server
mcp = MCPServer("GitHub MCP Server")


@mcp.tool()
def get_github_repo(owner: str, repo: str) -> dict:
    """
    Get information about a public GitHub repository.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(
            url,
            timeout=10
        )

    except requests.RequestException as e:
        return {
            "error": f"Could not connect to GitHub: {str(e)}"
        }

    if response.status_code == 404:
        return {
            "error": (
                f"Repository {owner}/{repo} "
                "was not found."
            )
        }

    if response.status_code != 200:
        return {
            "error": (
                f"GitHub API returned status "
                f"{response.status_code}"
            )
        }

    data = response.json()

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "open_issues": data.get("open_issues_count"),
        "url": data.get("html_url"),
    }


if __name__ == "__main__":
    # IMPORTANT:
    # MCP uses stdout for JSON-RPC communication.
    # Do NOT print anything to stdout here.

    mcp.run(transport="stdio")
