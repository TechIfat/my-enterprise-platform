from rich.console import Console
from rich.panel import Panel

console = Console()
import asyncio
import os
import json
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangGraph & AI Imports
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

load_dotenv()

server_params = StdioServerParameters(command="uv", args=["run", "finance_server.py"], env=None)

# 1. The State now tracks messages AND the "next" agent to route to
class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str

# 2. Pydantic Schema for Strict Supervisor Routing
# This forces the LLM to ONLY output one of these three exact strings.
class RouteDecision(BaseModel):
    next_agent: Literal["Market_Analyst", "Risk_Assessor", "FINISH"] = Field(
        description="The next agent to route to, or FINISH if the user's request is fully answered."
    )

async def run_multi_agent_loop(user_query: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_list = await session.list_tools()
            
            # Map tools by name for easy assignment
            tools_by_name = {t.name: t for t in tools_list.tools}
            
            def format_tool(tool):
                return {
                    "name": tool.name, 
                    "description": tool.description, 
                    "parameters": tool.inputSchema
                }

            # 3. Define the LLM
            llm = ChatAnthropic(model_name="claude-sonnet-4-6", temperature=0)

            # -----------------------------------------
            # NODE 1: THE SUPERVISOR
            # -----------------------------------------
            async def supervisor_node(state: State):
                print("👔 SUPERVISOR: Thinking about who should handle this...")
                system_prompt = SystemMessage(content="""You are a Banking Supervisor routing tasks. 
                Your team:
                - Market_Analyst: Retrieves stock prices.
                - Risk_Assessor: Evaluates company risk profiles AND checks internal compliance/trading policies.
                
                RULES:
                1. Review the conversation history. Worker agents will submit their reports to you as Human messages.
                2. If the user asks for a price, and there is NO report from the Market_Analyst, route to Market_Analyst.
                3. If the user asks for risk OR compliance rules, and there is NO report from the Risk_Assessor, route to Risk_Assessor.
                4. If the requested information is ALREADY in the chat history, output FINISH.
                """)
                
                messages = [system_prompt] + state["messages"]
                
                # We use structured_output to force Pydantic validation
                router_llm = llm.with_structured_output(RouteDecision)
                decision = await router_llm.ainvoke(messages)
                
                print(f"👔 SUPERVISOR DECISION: Route to -> {decision.next_agent}")
                return {"next": decision.next_agent}

            # -----------------------------------------
            # NODE 2: MARKET ANALYST (Specialist)
            # -----------------------------------------
            # Claude sometimes returns a list of blocks instead of a simple string. 
            # This cleans it up so our terminal UI stays beautiful.
            def extract_anthropic_text(content):
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Extract only the text blocks, ignore the raw tool_use JSON
                    return "\n".join(block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text")
                return str(content)

            # -----------------------------------------
            # NODE 2: MARKET ANALYST (Specialist)
            # -----------------------------------------
            async def market_analyst_node(state: State):
                print("📈 MARKET ANALYST: Analysing price data...")
                price_tool =[format_tool(tools_by_name["get_stock_price"])]
                agent_llm = llm.bind_tools(price_tool)
                
                response = await agent_llm.ainvoke(state["messages"])
                
                if response.tool_calls:
                    tool_messages =[]
                    for tool_call in response.tool_calls:
                        result = await session.call_tool(tool_call["name"], tool_call["args"])
                        tool_messages.append(ToolMessage(content=result.content[0].text, tool_call_id=tool_call["id"]))
                    
                    final_response = await agent_llm.ainvoke(state["messages"] + [response] + tool_messages)
                    
                    # CLEANUP CLAUDE'S OUTPUT
                    clean_text = extract_anthropic_text(final_response.content)
                    return {"messages":[HumanMessage(content=f"Market Analyst Report:\n{clean_text}", name="Market_Analyst")]}
                
                # CLEANUP CLAUDE'S OUTPUT (Fallback)
                clean_text = extract_anthropic_text(response.content)
                return {"messages":[HumanMessage(content=clean_text, name="Market_Analyst")]}

            # -----------------------------------------
            # NODE 3: RISK ASSESSOR (Specialist)
            # -----------------------------------------
            async def risk_assessor_node(state: State):
                print("🛡️ RISK ASSESSOR: Evaluating compliance and risk...")
                
                risk_tools = [
                    format_tool(tools_by_name["get_company_risk_profile"]),
                    format_tool(tools_by_name["search_internal_knowledge_base"])
                ]
                agent_llm = llm.bind_tools(risk_tools)
                
                # The Strict Persona
                system_prompt = SystemMessage(content="""You are the Chief Risk & Compliance Officer for the Bank.
                You MUST ALWAYS use the 'search_internal_knowledge_base' tool to check for internal trading limits, 
                Tier rules, or required sign-offs.
                
                CRITICAL FALLBACK RULE: 
                If the database tool returns "No relevant internal policies found", DO NOT hallucinate a policy. 
                You must explicitly state: "No specific internal compliance policy exists for this transaction. Standard market risk applies."
                """)
                
                messages_to_pass = [system_prompt] + state["messages"]
                response = await agent_llm.ainvoke(messages_to_pass)
                
                if response.tool_calls:
                    tool_messages =[]
                    for tool_call in response.tool_calls:
                        result = await session.call_tool(tool_call["name"], tool_call["args"])
                        tool_messages.append(ToolMessage(content=result.content[0].text, tool_call_id=tool_call["id"]))
                    
                    final_response = await agent_llm.ainvoke(messages_to_pass + [response] + tool_messages)
                    
                    # CLEANUP CLAUDE'S OUTPUT
                    clean_text = extract_anthropic_text(final_response.content)
                    return {"messages":[HumanMessage(content=f"Risk Assessor Report:\n{clean_text}", name="Risk_Assessor")]}
                
                # CLEANUP CLAUDE'S OUTPUT (Fallback)
                clean_text = extract_anthropic_text(response.content)
                return {"messages":[HumanMessage(content=clean_text, name="Risk_Assessor")]}
            # -----------------------------------------
            # BUILD THE MULTI-AGENT GRAPH
            # -----------------------------------------
            builder = StateGraph(State)
            
            builder.add_node("Supervisor", supervisor_node)
            builder.add_node("Market_Analyst", market_analyst_node)
            builder.add_node("Risk_Assessor", risk_assessor_node)

            # All worker nodes report back to the Supervisor
            builder.add_edge("Market_Analyst", "Supervisor")
            builder.add_edge("Risk_Assessor", "Supervisor")

            # The Supervisor's routing function checks the "next" state variable
            builder.add_conditional_edges(
                "Supervisor",
                lambda state: state["next"], # Reads the Pydantic output directly!
                {
                    "Market_Analyst": "Market_Analyst",
                    "Risk_Assessor": "Risk_Assessor",
                    "FINISH": END
                }
            )

            builder.add_edge(START, "Supervisor")

            # Compile with Memory
            async with AsyncSqliteSaver.from_conn_string("agent_memory.db") as memory:
                graph = builder.compile(checkpointer=memory)

                print("\n🏦 BANKING MULTI-AGENT SWARM ONLINE. Type 'quit' to exit.")
                # Added recursion_limit: If the graph hits 15 steps, it throws an error and stops burning tokens!
                config = {
                    "configurable": {"thread_id": "session_013"}, 
                    "recursion_limit": 15,
                }

                while True:
                    user_input = input("\n👤 YOU: ")
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                        
                    events = graph.astream({"messages": [HumanMessage(content=user_input)]}, config=config)
                    
                    async for event in events:
                        # Find the node name and the state update
                        for node_name, state_update in event.items():
                            if "messages" in state_update:
                                latest_msg = state_update["messages"][-1]
                                
                                # Format the output beautifully based on who is speaking
                                if node_name == "Supervisor":
                                    console.print(f"[bold magenta]👔 SUPERVISOR:[/bold magenta] Routing to {state_update.get('next', 'UNKNOWN')}")
                                elif node_name == "Market_Analyst":
                                    console.print(Panel(latest_msg.content, title="📈 MARKET ANALYST", border_style="green"))
                                elif node_name == "Risk_Assessor":
                                    console.print(Panel(latest_msg.content, title="🛡️ RISK ASSESSOR", border_style="red"))

if __name__ == "__main__":
    asyncio.run(run_multi_agent_loop(""))