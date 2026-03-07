import asyncio
import os
import json
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

load_dotenv()

# 1. Define the Server to Connect to
server_params = StdioServerParameters(
    command="uv",
    args=["run", "finance_server.py"],
    env=None
)

async def run_agent_loop(user_query: str):
    print(f"🤖 USER: {user_query}")
    
    # 2. Connect to the MCP Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # 3. Discover Tools
            await session.initialize()
            tools_list = await session.list_tools()
            
            # ARCHITECTURAL NOTE: 
            # We must convert MCP tool definitions to OpenAI's "Function Calling" format.
            openai_tools = []
            for tool in tools_list.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema # MCP schemas are JSON-schema compatible
                    }
                })
            
            print(f"🔌 Connected to Server. Found tools: {[t.name for t in tools_list.tools]}")

            # 4. Call the Brain (OpenAI)
            client = OpenAI()
            messages = [{"role": "user", "content": user_query}]
            
            response = client.chat.completions.create(
                model="gpt-4o", # Or gpt-3.5-turbo
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )

            # 5. Handle the LLM's Decision
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Append the model's decision to history
                messages.append(response_message)

                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🧠 GPT WANTS TO CALL: {func_name} with args {func_args}")

                    # 6. Execute Tool on Server
                    result = await session.call_tool(func_name, func_args)
                    print(f"🔧 TOOL RESULT: {result.content[0].text}")

                    # 7. Feed Result back to Brain
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text
                    })

                # 8. Final Answer
                final_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    tools=openai_tools
                )
                print(f"🤖 AGENT FINAL ANSWER: {final_response.choices[0].message.content}")
            else:
                print(f"🤖 AGENT: {response_message.content}")

if __name__ == "__main__":
    asyncio.run(run_agent_loop("What is the stock price of AAPL?"))