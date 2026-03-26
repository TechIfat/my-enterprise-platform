# ADR 012: Secure Transaction Execution via Legacy Integration and HITL Breakpoints

## Context
As the Enterprise Agentic Platform (EAP) moves beyond data retrieval into executing financial transactions, two critical risks emerge:
1. **Data Accuracy:** AI agents cannot rely on RAG (Vector Databases) for exact numeric state, such as real-time fiat cash balances.
2. **Fiduciary Risk:** Autonomous AI systems cannot be trusted with unsupervised write-access to financial ledgers. Hallucinations leading to unauthorized trades violate banking compliance.

## Decision
We implemented a dual-layered secure execution architecture:
1. **Legacy SQL Integration:** We exposed a local SQLite database (simulating a banking mainframe) via the MCP server. This grants the `Market_Analyst` deterministic read-access to exact account balances.
2. **Human-in-the-Loop (HITL) Breakpoints:** We isolated all state-changing actions into a dedicated `Trade_Executor` node. We applied a LangGraph execution breakpoint (`interrupt_before=["Trade_Executor"]`) to forcefully suspend the graph process prior to execution.

## Reasoning
* **Zero-Trust Execution:** The AI handles 99% of the analytical heavy lifting (verifying funds, routing to risk, assessing compliance), but the final 1% (the actual trade) is strictly locked behind a manual human override (`APPROVE`).
* **Bridging Brownfield Infrastructure:** By using MCP to query standard SQL, we prove the agentic swarm can safely interface with 40-year-old legacy banking mainframes without requiring a massive data-lake migration.
* **Auditability:** The pause in execution gives human compliance officers a complete, verifiable paper trail of the AI's reasoning *before* financial impact occurs.