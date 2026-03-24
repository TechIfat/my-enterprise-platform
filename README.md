# Enterprise Agentic Platform (EAP)

**Status:** Week 5 of 12 (In Active Development)
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
  - *ADR 002: Stateless Runtime vs. Stateful Orchestration.*
- [x] **Week 2: State & Orchestration (LangGraph)**
  - Migrated linear scripts to Directed Acyclic Graphs (DAGs) for multi-step reasoning.
  - Implemented Checkpointers for persistent memory.
  - *ADR 003: Checkpoint-based State Persistence.*
  - *ADR 004: Multi-Agent Supervisor Orchestration & Swarm Reliability.*
- [x] **Week 3: The Knowledge Layer (RAG) & API Gateway**
  - Implemented Decoupled RAG by hosting ChromaDB behind the MCP server to protect against prompt injection.
  - Exposed the LangGraph swarm via a FastAPI REST Gateway for frontend integration.
  - Migrated the core reasoning engine to Anthropic Claude 4.6 Sonnet for superior parallel tool execution.
  - *ADR 005: Decoupled RAG via Model Context Protocol*
  - *ADR 006: Orchestration Migration to Anthropic Claude 4.6 Sonnet*
- [x] **Week 4: The Developer Experience (SDK Design)**
  - Restructured repository to standard Python `src/` layout for enterprise packaging.
  - Built a unified Developer Experience (DX) using a global `eap` Typer CLI.
  - *ADR 007: Unified Developer Experience via Typer CLI*

### Phase 2: Governance, Security & Ops
- [x] **Week 5: Observability & Tracing (LangSmith)**
  - Integrated zero-code distributed tracing to track API latency, token costs, and multi-agent routing paths.
  - Enforced UK GDPR data residency by strictly routing telemetry to EU-West endpoints.
  - *ADR 008: Distributed Tracing & Observability via LangSmith (EU Data Residency)*
- [x] **Week 6: DevSecAI Guardrails (Shift-Left Security)**
  - Architected a decoupled Security Gateway node at the front of the LangGraph DAG.
  - Prevented prompt injections and roleplay jailbreaks from reaching the expensive LLM reasoning engine.
  - *ADR 009: Decoupled DevSecAI Gateway (Shift-Left Security)*
- [x] **Week 7: Eval-Driven Development (CI/CD)**
  - Built an automated integration testing pipeline (`run_evals.py`) to verify deterministic semantic boundaries.
  - Pipeline strictly blocks deployments (`exit code 1`) if agents suffer role-confusion or fail mandatory compliance triggers.
  - *ADR 010: Eval-Driven Development (EDD) and CI/CD Automation*
- [ ] **Week 8: Edge-Cloud Routing**

### Phase 3: Strategy & Advanced Patterns (Upcoming)
- [ ] **Week 9: Legacy Integration Patterns**
- [ ] **Week 10: Human-in-the-Loop (HITL) Workflows**
- [ ] **Week 11: Multi-Agent Consensus & Swarms**
- [ ] **Week 12: The Architect's Capstone (Reference Architecture)**

---

## 🚀 How to Run (Current State)

This project uses `uv` for lightning-fast dependency management and is packaged as a unified CLI tool. The Agent Runtime automatically spins up the MCP Nervous System as a subprocess.

**1. Clone and Sync Dependencies**
```bash
uv sync
```

**2. Configure Environment**
Create a .env file in the root directory. You will need both API keys (OpenAI is used for Vector Embeddings, Anthropic is used for the Orchestration Brain):

```Env
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**3. Run the Platform via CLI**
You can control the entire ecosystem using the eap command:

```Bash
# View all available commands
uv run eap --help

# Seed the Vector Database with enterprise policies
uv run eap seed

# Start the interactive Multi-Agent Swarm terminal
uv run eap chat

# Launch the production FastAPI REST Gateway (Swagger UI at http://localhost:8000/docs)
uv run eap serve
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
*(Note: This is an open-source portfolio project. Enterprise deployment requires independent security and compliance auditing).*

## 📬 Contact & Consulting

**Ifat Noreen**
*Principal Agentic AI Architect | DevSecAI Engineer*

* **LinkedIn:**[linkedin.com/in/ifat-noreen](https://www.linkedin.com/in/ifat-noreen)
* **GitHub:** [@TechIfat](https://github.com/TechIfat)
* **Inquiries:** Open to Staff/Principal engineering roles and enterprise AI consultancy.