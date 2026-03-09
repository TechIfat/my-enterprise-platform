# Enterprise Agentic Platform (EAP)

**Status:** Week 2 of 12 (In Active Development)
**Architect:** Ifat Noreen
**Target:** Building a production-grade, multi-agent ecosystem from first principles.

## The Initiative
This repository tracks a 12-week intensive build of an Enterprise Agentic Platform. The goal is to solve "Day 2 Operations" for AI agents: Reliability, Security, Orchestration, and Cost.

---

## 🏗️ Architecture & Progress Log

### Phase 1: The Runtime & Core Architecture
- [x] **Week 1: The Nervous System (MCP)**
  - Built a Model Context Protocol (MCP) server (`finance_server.py`) to decouple LLM logic from data tools.
  - Implemented initial stateless runtime.
  - *ADR 001: Adopted MCP for secure, scalable tool execution.*
- [ ] **Week 2: State & Orchestration (LangGraph)**
  - Migrating linear scripts to Directed Acyclic Graphs (DAGs) for multi-step reasoning.
  - Implementing Checkpointers for persistent memory.
- [ ] **Week 3: The Knowledge Layer (RAG)**
- [ ] **Week 4: The Developer Experience (SDK Design)**

### Phase 2: Governance, Security & Ops (Upcoming)
- [ ] **Week 5: Observability & Tracing (OpenTelemetry)**
- [ ] **Week 6: DevSecAI Guardrails (NVIDIA NeMo)**
-[ ] **Week 7: Eval-Driven Development**
- [ ] **Week 8: Edge-Cloud Routing**

### Phase 3: Strategy & Advanced Patterns (Upcoming)
- [ ] **Week 9: Legacy Integration Patterns**
- [ ] **Week 10: Human-in-the-Loop (HITL) Workflows**
- [ ] **Week 11: Multi-Agent Consensus & Swarms**
-[ ] **Week 12: The Architect's Capstone (Reference Architecture)**

---

## 🚀 How to Run (Current State)

This project uses `uv` for lightning-fast dependency management. The Agent Runtime automatically spins up the MCP Nervous System as a subprocess.

**1. Configure Environment**
Create a `.env` file in the root directory and add your key:
`OPENAI_API_KEY=sk-your-key-here`

**2. Run the Platform**
```bash
uv run agent.py
```
