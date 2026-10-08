import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq
from mcp import Client, StdioServerParameters


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing from the .env file."
    )


# ============================================================
# Create Groq client
# ============================================================

groq = Groq(api_key=api_key)


# ============================================================
# Convert MCP tools into Groq tool format
# ============================================================

def convert_tools(mcp_tools):
    tools = []

    for tool in mcp_tools:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
        )

    return tools


# ============================================================
# Convert MCP tool result into text
# ============================================================

def get_tool_result(result):
    text_parts = []

    for item in result.content:

        if hasattr(item, "text"):
            text_parts.append(item.text)

        else:
            try:
                text_parts.append(
                    json.dumps(item.model_dump())
                )

            except Exception:
                text_parts.append(str(item))

    return "\n".join(text_parts)


# ============================================================
# Main application
# ============================================================

async def main():

    print("\nConnecting to MCP server...")

    # --------------------------------------------------------
    # Start MCP server using the same Python environment
    # --------------------------------------------------------

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
    )

    # --------------------------------------------------------
    # Connect MCP client to MCP server
    # --------------------------------------------------------

    async with Client(server_params) as mcp:

        print("Connected to MCP server.")

        # ----------------------------------------------------
        # Discover available MCP tools
        # ----------------------------------------------------

        tool_response = await mcp.list_tools()

        mcp_tools = tool_response.tools

        print("\nAvailable MCP tools:")

        for tool in mcp_tools:
            print(f"  - {tool.name}")

        # ----------------------------------------------------
        # Convert MCP tools to Groq format
        # ----------------------------------------------------

        groq_tools = convert_tools(mcp_tools)

        # ----------------------------------------------------
        # Ask the user
        # ----------------------------------------------------

        question = input(
            "\nAsk something about GitHub: "
        )

        # ----------------------------------------------------
        # Initial conversation
        # ----------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful GitHub assistant. "
                    "When the user asks about a GitHub repository, "
                    "use the available MCP tool. "
                    "If the user gives a repository as owner/repo, "
                    "extract the owner and repository name."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        # ----------------------------------------------------
        # First Groq call
        #
        # The LLM decides whether it needs the MCP tool.
        # ----------------------------------------------------

        print("\nSending request to Groq...")

        response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # If LLM doesn't request a tool
        # ----------------------------------------------------

        if not assistant_message.tool_calls:

            print("\n====================================")
            print("ASSISTANT")
            print("====================================\n")

            print(assistant_message.content)

            return

        # ----------------------------------------------------
        # Process the requested MCP tool
        # ----------------------------------------------------

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"\nLLM requested MCP tool: "
                f"{tool_name}"
            )

            print(
                f"Arguments: {arguments}"
            )

            # ------------------------------------------------
            # Call MCP server
            # ------------------------------------------------

            print("\nCalling MCP server...")

            result = await mcp.call_tool(
                tool_name,
                arguments
            )

            print(
                "MCP tool executed successfully."
            )

            # ------------------------------------------------
            # Extract result
            # ------------------------------------------------

            tool_result = get_tool_result(result)

            print("\nGitHub result received.")

            # ------------------------------------------------
            # IMPORTANT:
            #
            # We don't send the original tool conversation
            # back to Groq.
            #
            # Instead, we give Groq the GitHub data in a new
            # simple prompt.
            #
            # This prevents the model from trying to call
            # another tool such as repo_browser.get_tree.
            # ------------------------------------------------

            print(
                "\nSending GitHub information "
                "back to the LLM..."
            )

            final_prompt = f"""
Answer the user's question using the GitHub information
retrieved through the MCP server.

User question:
{question}

GitHub information:
{tool_result}

Give a clear and concise answer.

Do not call any tools.
Use only the GitHub information provided above.
"""

            # ------------------------------------------------
            # Second Groq call
            # ------------------------------------------------

            final_response = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful GitHub assistant. "
                            "Answer the user's question using "
                            "only the GitHub information provided. "
                            "Do not call tools."
                        ),
                    },
                    {
                        "role": "user",
                        "content": final_prompt,
                    },
                ],
            )

            # ------------------------------------------------
            # Display final answer
            # ------------------------------------------------

            print("\n====================================")
            print("ASSISTANT")
            print("====================================\n")

            print(
                final_response
                .choices[0]
                .message
                .content
            )


# ============================================================
# Start application
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
