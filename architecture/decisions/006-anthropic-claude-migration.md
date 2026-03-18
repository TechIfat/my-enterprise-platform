# ADR 006: Orchestration Migration to Anthropic Claude 4.6 Sonnet

## Context
As the Enterprise Agentic Platform (EAP) scales, the orchestration layer requires an LLM with superior native support for the Model Context Protocol (MCP), highly reliable parallel tool calling, and deterministic multi-agent routing. 

## Decision
We migrated the core orchestration engine (Supervisor and Specialist nodes) from OpenAI `gpt-4o` to Anthropic `claude-sonnet-4-6` via LangChain. 
*Note: Vector embedding generation remains on OpenAI to maintain historical ChromaDB compatibility, proving our loosely-coupled architectural design.*

## Reasoning
* **Native MCP Alignment:** Anthropic leads the development of the open-source Model Context Protocol. Using Claude ensures frictionless, zero-latency integration with our FastMCP enterprise data servers.
* **Complex Tool Use:** Claude 4.6 Sonnet demonstrates significantly lower hallucination rates when dealing with "Null States" (e.g., when a RAG database returns empty results) and handles parallel tool schemas more deterministically.
* **Vendor Agnosticism:** By swapping the orchestration engine in exactly two lines of code, we validated that our LangGraph architecture is entirely model-agnostic, preventing enterprise vendor lock-in.