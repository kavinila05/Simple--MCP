# GitHub MCP Demo

A simple, real-world demonstration of **Model Context Protocol (MCP)** using a Groq LLM and the GitHub REST API.

This project demonstrates how an LLM can decide to use an external tool through an MCP Client and MCP Server.

The goal is to understand MCP from the ground up without adding unnecessary frameworks or complexity.

---

## What is MCP?

**MCP (Model Context Protocol)** is a standard protocol that allows AI applications to connect to external tools, data sources, and services in a consistent way.

Instead of building every external integration directly inside an AI application, an MCP Server can expose capabilities as tools.

For example:

```text
AI Application
      |
      | MCP
      |
      v
MCP Server
      |
      +---- GitHub API
      +---- Database
      +---- Files
      +---- Internal APIs
```

The AI application can discover the tools provided by the MCP Server and invoke them when required.

### Simple analogy

Think of MCP as a standard interface between an AI application and external capabilities.

The AI application does not need to know the internal implementation of every external service.

It only needs to understand:

```text
What tools are available?
What arguments do they require?
How do I call them?
What result did they return?
```

---

# What does this project demonstrate?

This project demonstrates:

- LLM-based tool selection
- MCP Client
- MCP Server
- MCP tool discovery
- MCP tool invocation
- GitHub REST API integration
- Groq function/tool calling
- Passing external tool results back to an LLM
- Generating a natural-language response from external data

---

# Architecture

The complete flow is:

```text
                         USER
                           |
                           |
                           v
                    +-------------+
                    |  Groq LLM   |
                    |             |
                    | Understands |
                    | the request |
                    +------+------+
                           |
                           |
                    Tool decision
                           |
                           v
                    +-------------+
                    | MCP Client  |
                    |             |
                    | Discovers   |
                    | MCP tools   |
                    +------+------+
                           |
                           | MCP
                           |
                           v
                    +-------------+
                    | MCP Server  |
                    |             |
                    | get_github_ |
                    | repo()      |
                    +------+------+
                           |
                           |
                           v
                    +-------------+
                    | GitHub API  |
                    +------+------+
                           |
                           |
                      Repository
                        data
                           |
                           v
                    +-------------+
                    |  Groq LLM   |
                    |             |
                    | Summarizes  |
                    | the result  |
                    +------+------+
                           |
                           v
                      FINAL ANSWER
```

---

# Project Structure

```text
github-mcp-demo/
│
├── client.py
├── server.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── venv/
```

> `venv/` should not be committed to GitHub.

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application language |
| Groq | LLM and tool calling |
| MCP | Standardized communication between AI application and tools |
| GitHub REST API | External data source |
| Requests | HTTP communication with GitHub |
| python-dotenv | Loading environment variables |
| asyncio | Running the MCP client asynchronously |

---

# Required Versions

This project was developed and tested using:

```text
Python 3.11
MCP 2.3.x
```

The project currently specifies:

```text
mcp>=2.3,<3
```

in `requirements.txt`.

This means the project uses the **MCP 2.x Python SDK** and prevents installation of MCP 3.x versions.

The remaining dependencies are:

```text
groq
python-dotenv
requests
```

The exact versions of these packages can be installed by running:

```bash
pip install -r requirements.txt
```

---

# Prerequisites

Before running the project, install:

1. Python 3.11
2. Git
3. A GitHub account
4. A Groq API key

You do **not** need a GitHub API token for this demo because the project only reads information from a public GitHub repository.

---

# 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project:

```bash
cd github-mcp-demo
```

---

# 2. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

You should see:

```text
(venv)
```

in your terminal.

---

# 3. Install Dependencies

Run:

```powershell
pip install -r requirements.txt
```

This installs:

```text
MCP
Groq
python-dotenv
Requests
```

---

# 4. Configure the Groq API Key

Create a file named:

```text
.env
```

Add:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Example:

```text
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxx
```

Do **not** commit this file to GitHub.

The `.gitignore` file should contain:

```text
.env
venv/
__pycache__/
*.pyc
```

---

# 5. Create `.env.example`

For GitHub, commit an example file instead:

```text
GROQ_API_KEY=your_groq_api_key_here
```

This allows other developers to understand what environment variable is required without exposing your actual API key.

---

# How the Code Works

## `server.py`

The MCP Server exposes a tool called:

```python
get_github_repo(owner, repo)
```

The tool calls:

```text
https://api.github.com/repos/{owner}/{repo}
```

and returns useful repository information such as:

- Repository name
- Full repository name
- Description
- Stars
- Forks
- Programming language
- Open issues
- GitHub URL

The MCP tool is defined using:

```python
@mcp.tool()
def get_github_repo(owner: str, repo: str) -> dict:
```

This makes the function available to MCP clients.

---

# `client.py`

The client performs several steps.

## Step 1 — Connect to MCP Server

The client starts:

```text
server.py
```

as an MCP server process.

```text
client.py
    |
    | starts
    v
server.py
```

---

## Step 2 — Discover MCP Tools

The client asks the MCP server for its available tools.

Conceptually:

```text
Client
   |
   | list_tools()
   |
   v
MCP Server
   |
   +--> get_github_repo
```

The client discovers:

```text
get_github_repo
```

---

## Step 3 — Give the Tool to the LLM

The MCP tool definition is converted into the format expected by Groq tool calling.

The LLM can then see something conceptually like:

```text
Tool:
get_github_repo

Arguments:
owner
repo
```

---

## Step 4 — User Asks a Question

Example:

```text
Tell me about the GitHub repository kavinila05/RBAC-RAG
```

The LLM determines that it needs GitHub information.

It produces a tool call similar to:

```json
{
  "name": "get_github_repo",
  "arguments": {
    "owner": "kavinila05",
    "repo": "RBAC-RAG"
  }
}
```

---

# Step 5 — MCP Client Calls the MCP Server

The client receives the LLM's tool request.

It then calls:

```python
await mcp.call_tool(
    "get_github_repo",
    {
        "owner": "kavinila05",
        "repo": "RBAC-RAG"
    }
)
```

The MCP server executes the actual Python function.

---

# Step 6 — MCP Server Calls GitHub

The MCP server makes the HTTP request:

```text
MCP Server
     |
     v
GitHub REST API
     |
     v
Repository information
```

For example:

```json
{
  "name": "RBAC-RAG",
  "full_name": "kavinila05/RBAC-RAG",
  "language": "Python",
  "stars": 0,
  "forks": 1
}
```

---

# Step 7 — Send the Result to the LLM

The GitHub result is passed to Groq.

The LLM converts the raw data into a human-readable response.

For example:

```text
The repository kavinila05/RBAC-RAG is a Python project
focused on implementing Role-Based Access Control in a
Retrieval-Augmented Generation workflow...
```

---

# Why Use MCP Here?

Without MCP, the application could simply call GitHub directly:

```text
LLM
 |
 v
Python function
 |
 v
GitHub API
```

That is normal tool calling.

With MCP:

```text
LLM
 |
 v
MCP Client
 |
 | MCP
 v
MCP Server
 |
 v
GitHub API
```

The important difference is that the external capability is exposed through a **standardized MCP interface**.

---

# MCP vs Agent Tool Calling

MCP and agent tool calling are related, but they are not the same thing.

### Agent Tool Calling

Tool calling allows an LLM to request execution of a function.

For example:

```python
def get_github_repo(owner, repo):
    ...
```

The LLM decides:

```text
I need get_github_repo
```

and the application executes it.

---

### MCP

MCP provides a standardized protocol for exposing and accessing tools and other external capabilities.

Instead of the AI application directly owning every integration:

```text
AI Application
 |
 +-- GitHub function
 +-- Database function
 +-- Slack function
 +-- Jira function
```

we can have:

```text
                 AI Application
                       |
                      MCP
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
   GitHub MCP     Database MCP    Other MCP
      Server          Server        Server
```

So:

```text
Agent
    = decides what action to take

Tool Calling
    = mechanism for requesting a tool execution

MCP
    = standardized protocol for connecting AI applications
      with external tools/context
```

---

# MCP vs RAG

MCP and RAG solve different problems.

## RAG

RAG is primarily about retrieving relevant information before generating an answer.

Typical RAG:

```text
Documents
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
Vector Database
    |
    v
Retriever
    |
    v
Relevant Context
    |
    v
LLM
```

---

## MCP

MCP is about connecting an AI application to external capabilities.

For example:

```text
AI Application
      |
     MCP
      |
      +--- GitHub
      +--- Database
      +--- Files
      +--- APIs
```

They can also be combined:

```text
                    LLM / Agent
                         |
                        MCP
                         |
              +----------+----------+
              |                     |
              v                     v
         MCP RAG Server       MCP GitHub Server
              |                     |
              v                     v
          Vector DB             GitHub API
```

---

# Is This an Agentic RAG Project?

No.

This project is intentionally smaller.

It demonstrates:

```text
LLM
 +
Tool Calling
 +
MCP Client
 +
MCP Server
 +
GitHub API
```

It does not implement a traditional RAG pipeline because there is no:

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Database
    ↓
Retrieval
```

The purpose of this project is to understand MCP independently before combining it with Agentic RAG.

---

# Example

Run:

```powershell
python client.py
```

You will see:

```text
Connecting to MCP server...
Connected to MCP server.

Available MCP tools:
  - get_github_repo
```

Enter:

```text
Tell me about the GitHub repository kavinila05/RBAC-RAG
```

The application then performs:

```text
User question
      ↓
Groq LLM
      ↓
Tool selection
      ↓
MCP Client
      ↓
MCP Server
      ↓
get_github_repo()
      ↓
GitHub REST API
      ↓
Repository information
      ↓
Groq LLM
      ↓
Final answer
```

---

# Important Security Notes

Never commit:

```text
.env
```

or any file containing your API key.

Use:

```text
.env
```

locally and:

```text
.env.example
```

in GitHub.

If an API key is accidentally pushed to GitHub, revoke it immediately and generate a new key.

---

# Troubleshooting

## `GROQ_API_KEY is missing`

Make sure `.env` exists in the project root:

```text
github-mcp-demo/
├── .env
├── client.py
└── server.py
```

and contains:

```text
GROQ_API_KEY=your_actual_key
```

---

## MCP JSON-RPC parsing errors

MCP uses `stdout` for protocol communication when using the `stdio` transport.

The MCP server should not contain debugging statements such as:

```python
print("Server started")
```

because this can interfere with JSON-RPC messages.

Use logging to `stderr` instead if debugging is required.

---

## Connection closed / MCP server timeout

Check:

```text
Python version
MCP version
server.py
client.py
```

Recommended environment for this project:

```text
Python 3.11
MCP 2.x
```

Verify MCP:

```powershell
pip show mcp
```

---

# Future Improvements

Possible extensions to this project:

- Add more GitHub tools
- Get repository files
- Search GitHub repositories
- Read GitHub issues
- Create GitHub issues
- Add multiple MCP servers
- Add an Agentic RAG MCP server
- Connect ChromaDB through MCP
- Add Slack/Jira/database MCP integrations
- Build a multi-tool AI agent
- Add a Streamlit UI

A future architecture could look like:

```text
                         USER
                           |
                           v
                     AI AGENT / LLM
                           |
                          MCP
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      GitHub MCP       RAG MCP          Database MCP
        Server          Server             Server
          |                |                |
          v                v                v
       GitHub          ChromaDB          Database
```

---

# Learning Goal

This project was built to understand the relationship between:

```text
LLMs
   ↓
Tool Calling
   ↓
Agents
   ↓
MCP
   ↓
External APIs
   ↓
RAG
```

The main takeaway is:

> **MCP does not replace agents, tool calling, or RAG. It provides a standardized way for AI applications to interact with external tools and data sources.**

---

# License

This project is intended for learning and demonstration purposes.
