ADR 001: Adoption of Model Context Protocol (MCP)

Context:
We need to connect LLMs to internal financial data tools.

Options:
Proprietary OpenAI Function Calling (Locked to GPT models).
LangChain Tools (Python-specific, hard to share across languages).
Model Context Protocol (Open standard, Client-Server model).

Decision:
We will use MCP.

Reasoning:

Decoupling: The "Finance Tool" server can be maintained by the Data Team in Python, while the "Agent" can be swapped from Claude to GPT-4 without rewriting tool logic.
Security: Tools run in their own process/container, isolating them from the LLM's memory space.
Future Proofing: Supported by Anthropic, Replit, and growing ecosystem.

