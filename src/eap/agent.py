from eap.security.firewall import EnterpriseFirewall
import uuid
import asyncio
import os
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

load_dotenv()
console = Console()

server_params = StdioServerParameters(
    command="python", 
    args=["-m", "eap.finance_server"], 
    env=os.environ
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str

class RouteDecision(BaseModel):
    next_agent: Literal["Market_Analyst", "Risk_Assessor", "FINISH"] = Field(
        description="The next agent to route to, or FINISH if the user's request is fully answered."
    )

def format_tool(tool):
    return {"name": tool.name, "description": tool.description, "parameters": tool.inputSchema}

def extract_anthropic_text(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "\n".join(block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text")
    return str(content)

# --- NEW: SINGLE SOURCE OF TRUTH FOR THE GRAPH ---
async def build_agent_graph(session: ClientSession, memory: AsyncSqliteSaver):
    """Builds and compiles the LangGraph swarm, sharing it across CLI and API."""
    tools_list = await session.list_tools()
    tools_by_name = {t.name: t for t in tools_list.tools}
    
    # Using your custom working model string!
    llm = ChatAnthropic(model_name="claude-sonnet-4-6", temperature=0) 

    # -----------------------------------------
    # NODE 0: THE SECURITY OFFICER (Firewall)
    # -----------------------------------------
    async def security_node(state: State):
        print("🛡️ SECURITY OFFICER: Scanning prompt via Enterprise Firewall...")
        
        # The AI team just initializes the firewall the DevSecOps team built!
        firewall = EnterpriseFirewall(llm)
        decision = await firewall.scan_prompt(state["messages"][-1].content, state["messages"])
        
        if not decision.is_safe:
            console.print(f"[bold red]🚨 SECURITY ALERT:[/bold red] {decision.reason}")
            return {
                "messages":[AIMessage(content=f"SECURITY BLOCK: {decision.reason}", name="Security_Officer")],
                "next": "FINISH"
            }
        
        print("✅ SECURITY CLEARANCE: Safe to proceed.")
        return {"next": "Supervisor"}

    # -----------------------------------------
    # NODE 1: THE SUPERVISOR (Routing Decision Maker)
    # -----------------------------------------
    async def supervisor_node(state: State):
        system_prompt = SystemMessage(content="""You are a Banking Supervisor routing tasks. 
        Your team: Market_Analyst and Risk_Assessor.
        RULES:
        1. Review history. Worker agents submit reports as Human messages.
        2. If price needed and no Analyst report, route to Market_Analyst.
        3. If risk/compliance needed and no Assessor report, route to Risk_Assessor.
        4. If information is ALREADY in chat history, output FINISH.
        """)
        router_llm = llm.with_structured_output(RouteDecision)
        decision = await router_llm.ainvoke([system_prompt] + state["messages"])
        return {"next": decision.next_agent}

    # -----------------------------------------
    # NODE 2: THE MARKET ANALYST (Stock Price Research)
    # -----------------------------------------
    async def market_analyst_node(state: State):
        agent_llm = llm.bind_tools([format_tool(tools_by_name["get_stock_price"])])
        response = await agent_llm.ainvoke(state["messages"])
        
        if response.tool_calls:
            tool_msgs =[]
            for tc in response.tool_calls:
                result = await session.call_tool(tc["name"], tc["args"])
                tool_msgs.append(ToolMessage(content=result.content[0].text, tool_call_id=tc["id"]))
            final_response = await agent_llm.ainvoke(state["messages"] + [response] + tool_msgs)
            clean_text = extract_anthropic_text(final_response.content)
            return {"messages":[HumanMessage(content=f"Market Analyst Report:\n{clean_text}", name="Market_Analyst")]}
            
        clean_text = extract_anthropic_text(response.content)
        return {"messages":[HumanMessage(content=clean_text, name="Market_Analyst")]}

    # -----------------------------------------
    # NODE 3: THE RISK ASSESSOR (Compliance & Risk Check)
    # -----------------------------------------
    async def risk_assessor_node(state: State):
        risk_tools = [
            format_tool(tools_by_name["get_company_risk_profile"]),
            format_tool(tools_by_name["search_internal_knowledge_base"])
        ]
        agent_llm = llm.bind_tools(risk_tools)
        
        sys_msg = SystemMessage(content="""You are the Chief Risk & Compliance Officer for the Bank.
        You MUST ALWAYS use the 'search_internal_knowledge_base' tool to check for internal trading limits.
        CRITICAL FALLBACK RULE: If the database tool returns "No relevant internal policies found", DO NOT hallucinate a policy. Explicitly state: "No specific internal compliance policy exists for this transaction. Standard market risk applies."
        """)
        
        response = await agent_llm.ainvoke([sys_msg] + state["messages"])
        
        if response.tool_calls:
            tool_msgs =[]
            for tc in response.tool_calls:
                result = await session.call_tool(tc["name"], tc["args"])
                tool_msgs.append(ToolMessage(content=result.content[0].text, tool_call_id=tc["id"]))
            final_response = await agent_llm.ainvoke([sys_msg] + state["messages"] +[response] + tool_msgs)
            clean_text = extract_anthropic_text(final_response.content)
            return {"messages":[HumanMessage(content=f"Risk Assessor Report:\n{clean_text}", name="Risk_Assessor")]}
            
        clean_text = extract_anthropic_text(response.content)
        return {"messages": [HumanMessage(content=clean_text, name="Risk_Assessor")]}

    builder = StateGraph(State)
    
    # Add all 4 nodes
    builder.add_node("Security_Officer", security_node)
    builder.add_node("Supervisor", supervisor_node)
    builder.add_node("Market_Analyst", market_analyst_node)
    builder.add_node("Risk_Assessor", risk_assessor_node)

    # Edge logic
    builder.add_edge("Market_Analyst", "Supervisor")
    builder.add_edge("Risk_Assessor", "Supervisor")

    # The Security Routing logic
    builder.add_conditional_edges(
        "Security_Officer",
        lambda state: state["next"],
        {"Supervisor": "Supervisor", "FINISH": END}
    )

    # The Supervisor Routing logic
    builder.add_conditional_edges(
        "Supervisor",
        lambda state: state["next"], 
        {
            "Market_Analyst": "Market_Analyst",
            "Risk_Assessor": "Risk_Assessor",
            "FINISH": END
        }
    )

    # START goes to Security FIRST, not the Supervisor!
    builder.add_edge(START, "Security_Officer")

    return builder.compile(checkpointer=memory)

# --- CLI ENTRYPOINT ---
async def run_multi_agent_loop(user_query: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            async with AsyncSqliteSaver.from_conn_string("agent_memory.db") as memory:
                graph = await build_agent_graph(session, memory)
                
                # Generate a unique 8-character ID for every new terminal launch
                current_session = f"session_{uuid.uuid4().hex[:8]}"
                print(f"\n🏦 BANKING MULTI-AGENT SWARM ONLINE. [Session: {current_session}] Type 'quit' to exit.")
                
                config = {"configurable": {"thread_id": current_session}, "recursion_limit": 15}
                while True:
                    user_input = input("\n👤 YOU: ")
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                        
                    events = graph.astream({"messages": [HumanMessage(content=user_input)]}, config=config)
                    async for event in events:
                        for node_name, state_update in event.items():
                            if "messages" in state_update:
                                latest_msg = state_update["messages"][-1]
                                if node_name == "Supervisor":
                                    console.print(f"[bold magenta]👔 SUPERVISOR:[/bold magenta] Routing to {state_update.get('next', 'UNKNOWN')}")
                                elif node_name == "Market_Analyst":
                                    console.print(Panel(latest_msg.content, title="📈 MARKET ANALYST", border_style="green"))
                                elif node_name == "Risk_Assessor":
                                    console.print(Panel(latest_msg.content, title="🛡️ RISK ASSESSOR", border_style="red"))

# --- API ENTRYPOINT ---
async def get_agent_response(user_query: str, thread_id: str) -> str:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            async with AsyncSqliteSaver.from_conn_string("agent_memory.db") as memory:
                graph = await build_agent_graph(session, memory)
                config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 15}
                
                events = graph.astream({"messages": [HumanMessage(content=user_query)]}, config=config, stream_mode="values")
                final_state = None
                async for event in events:
                    final_state = event
                
                return extract_anthropic_text(final_state["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(run_multi_agent_loop(""))