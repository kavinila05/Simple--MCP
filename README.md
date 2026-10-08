# GitHub MCP Assistant

A small demo showing **LLM + MCP + GitHub API** working together.

## Architecture

User
  |
  v
Groq LLM
  |
  | decides to use a tool
  v
MCP Client
  |
  | MCP protocol
  v
MCP Server
  |
  | get_github_repo()
  v
GitHub REST API
  |
  v
Repository data
  |
  v
MCP Client -> Groq -> final answer

## What it does

Ask a question such as:

    Tell me about the GitHub repository kavinila05/RBAC-RAG

The LLM identifies that GitHub information is needed, requests the
`get_github_repo` MCP tool, the MCP server calls GitHub, and the result
is returned to the LLM for a natural-language answer.

## Requirements

- Python 3.10+
- A Groq API key
- Internet connection

## Setup

### 1. Create a virtual environment

Windows:

    python -m venv venv
    venv\Scripts\activate

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Create `.env`

Copy `.env.example` to `.env` and add your Groq key:

    GROQ_API_KEY=your_real_key_here

Do not commit `.env` to GitHub.

### 4. Run

    python client.py

Then enter a GitHub repository question.

Example:

    Tell me about the GitHub repository kavinila05/RBAC-RAG

## MCP concepts demonstrated

### MCP Server

`server.py` exposes the GitHub functionality.

### MCP Tool

This decorator turns the Python function into an MCP tool:

    @mcp.tool()
    def get_github_repo(owner: str, repo: str):
        ...

### MCP Client

`client.py` connects to the server using the local `stdio` transport.

### Tool discovery

The client discovers the tools with:

    await session.list_tools()

### Tool execution

The client calls the tool requested by the LLM with:

    await session.call_tool(tool_name, arguments)

## Important point for the demo

The LLM does NOT directly call the GitHub API.

The flow is:

    LLM
      |
      v
    MCP Client
      |
      v
    MCP Server
      |
      v
    GitHub API

This separation is the main concept you are demonstrating.

## Demo talking points

1. The MCP server exposes a GitHub capability as a tool.
2. The MCP client discovers that tool.
3. The tool schema is passed to the LLM.
4. The LLM decides whether it needs the tool.
5. The client executes the MCP tool.
6. The server calls GitHub.
7. The result goes back through MCP to the LLM.
8. The LLM produces the final answer.

## Limitations

This is intentionally a simple learning/demo project.

- It reads public GitHub repository information.
- It does not modify GitHub repositories.
- It does not require a GitHub token.
- It has only one MCP tool.
- It uses a local `stdio` MCP connection.

## Next possible upgrade

Add another tool such as:

    search_github_repositories()

Then the assistant could search for a repository first and inspect it second.
