import asyncio
import os
import json
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- NEW LANGGRAPH IMPORTS ---
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# 1. Define the Server to Connect to (The Nervous System)
server_params = StdioServerParameters(
    command="uv",
    args=["run", "finance_server.py"],
    env=None
)

# 2. Define the State (The Graph's Memory)
# This dictates what data is passed between nodes.
class State(TypedDict):
    # add_messages is a reducer: it appends new messages to the existing list
    messages: Annotated[list, add_messages]

async def run_agent_loop(user_query: str):
    print(f"\n🤖 USER: {user_query}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # --- INITIALIZE MCP TOOLS ---
            await session.initialize()
            tools_list = await session.list_tools()
            
            # Convert MCP tools to OpenAI format
            openai_tools =[]
            for tool in tools_list.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            print(f"🔌 Connected to MCP. Found tools: {[t.name for t in tools_list.tools]}")

            # --- BUILD THE GRAPH NODES ---
            
            # Node 1: The Brain (LLM)
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            llm_with_tools = llm.bind_tools(openai_tools)

            async def chatbot_node(state: State):
                """Calls the LLM and appends the response to the state."""
                response = await llm_with_tools.ainvoke(state["messages"])
                return {"messages": [response]}

            # Node 2: The Hands (Tool Execution)
            async def tool_node(state: State):
                """Executes MCP tools and appends results to the state."""
                last_message = state["messages"][-1]
                tool_results =[]
                
                # Loop through all tools the LLM decided to call
                for tool_call in last_message.tool_calls:
                    func_name = tool_call["name"]
                    func_args = tool_call["args"]
                    print(f"🧠 GRAPH ROUTING: Executing tool -> {func_name}({func_args})")
                    
                    # Call the actual MCP server
                    result = await session.call_tool(func_name, func_args)
                    
                    # Format result for LangGraph
                    tool_results.append(
                        ToolMessage(
                            content=result.content[0].text,
                            tool_call_id=tool_call["id"]
                        )
                    )
                return {"messages": tool_results}

            # --- BUILD THE GRAPH EDGES (ROUTING LOGIC) ---
            def route_tools(state: State):
                """Decides if we need to use a tool, or if we are done."""
                last_message = state["messages"][-1]
                if last_message.tool_calls:
                    return "tools"
                return END

            # --- COMPILE THE GRAPH ---
            graph_builder = StateGraph(State)
            graph_builder.add_node("chatbot", chatbot_node)
            graph_builder.add_node("tools", tool_node)
            
            # Define the flow
            graph_builder.add_edge(START, "chatbot")
            graph_builder.add_conditional_edges("chatbot", route_tools, {"tools": "tools", END: END})
            graph_builder.add_edge("tools", "chatbot") # Loop back to chatbot after tool runs
            
            graph = graph_builder.compile()

            # --- RUN THE GRAPH ---
            initial_state = {"messages":[HumanMessage(content=user_query)]}
            
            # We use astream to watch the graph execute step-by-step
            async for event in graph.astream(initial_state):
                for node_name, node_state in event.items():
                    print(f"✅ Finished Node: '{node_name}'")
            
            # Print Final Output
            final_message = node_state["messages"][-1]
            print(f"\n🤖 AGENT FINAL ANSWER: {final_message.content}")

if __name__ == "__main__":
    # A complex query that requires MULTIPLE steps
    query = "What is the stock price of AAPL? And based on its risk profile, is it a safe bet?"
    asyncio.run(run_agent_loop(query))