# ADR 003: Checkpoint-based State Persistence

## Context
Enterprise multi-agent systems require state recovery for human-in-the-loop workflows, system crashes, and multi-turn conversations. Relying on in-memory arrays (RAM) violates reliability standards.

## Decision
We will use LangGraph's native Checkpointer architecture, specifically `AsyncSqliteSaver` for local development (which maps perfectly to PostgreSQL for production).

## Reasoning
* **Thread Isolation:** The `thread_id` configuration allows us to securely isolate different users/sessions within the same database.
* **Time Travel:** Checkpointing saves every *step* of the graph, not just the final output. This enables auditing and debugging.
* **Stateless Compute:** Worker nodes can scale horizontally and die without losing customer session data.