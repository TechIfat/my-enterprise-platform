ADR 002: Stateless Runtime vs. Stateful Orchestration

Context:
We connected an LLM directly to MCP tools using a simple request-response pattern.

Decision:
We will adopt a Loop-based Architecture (using LangGraph in future) rather than a linear script.

Reasoning:
- Multi-Step Reasoning: Real-world tasks (e.g., "Research this company") require multiple tool calls in sequence.
- Error Recovery: If a tool fails (e.g., API timeout), the Agent needs to see the error and retry, rather than the script crashing.
- State Persistence: We need to save the conversation history to a database (Postgres) so the user can pause and resume later.