# ADR 004: Multi-Agent Supervisor Orchestration & Swarm Reliability

## Context
A single "God Agent" with access to all enterprise tools violates the Principle of Least Privilege and suffers from context-window degradation. However, moving to a Multi-Agent Swarm introduces new distributed system risks, such as infinite routing loops and API parallel execution failures.

## Decision
We will implement a LangGraph Multi-Agent Supervisor Pattern utilizing `Pydantic` for deterministic routing, coupled with strict "Defense in Depth" reliability patterns.

## Reasoning
* **Blast Radius Isolation:** The Market Analyst cannot accidentally trigger Risk protocols, as tools are physically bound only to specific specialist nodes.
* **Deterministic Routing:** By forcing the Supervisor to output a strict Pydantic `Literal`, we eliminate hallucinated routing paths.
* **State Identity (Anti-Loop):** Worker agents must return their outputs as `HumanMessage` (with a `name` attribute) rather than `AIMessage`. This prevents the Supervisor from confusing a worker's report with its own internal monologue, effectively solving infinite recursive routing.
* **Circuit Breakers:** We enforce a hard `recursion_limit` at the graph execution level to automatically kill the process if the swarm gets stuck, preventing catastrophic API token burn.
* **Parallel Tool Execution:** Worker nodes are architected to loop through and execute *all* requested tool calls before returning to the LLM. This prevents 400 Bad Request errors from strict providers like OpenAI.