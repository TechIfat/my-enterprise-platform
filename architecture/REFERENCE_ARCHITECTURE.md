# Enterprise Agentic Platform (EAP) - Reference Architecture
**Version:** 1.0.0 | **Status:** Production-Ready | **Architect:** Ifat Noreen

## 1. System Overview
The EAP is a stateful, DevSecOps-hardened multi-agent orchestration engine designed for the Banking and Fintech sectors. It bridges the gap between non-deterministic Large Language Models (LLMs) and strictly deterministic legacy banking infrastructure.

## 2. Core Architectural Pillars

### A. Orchestration Layer (LangGraph)
* **Directed Acyclic Graph (DAG):** Replaces linear agent scripts with cyclic graphs, enabling multi-step reasoning, autonomous error recovery, and strict state management.
* **Semantic Triage (Edge-Cloud Routing):** Ingress prompts are evaluated by a low-latency model (`claude-3-haiku`). Simple queries are resolved at the edge, while complex financial tasks are routed to the core reasoning engine (`claude-4.6-sonnet`), reducing API costs by ~90%.
* **Consensus Pattern:** Critical path decisions utilise a "Maker-Checker" topology. The `Risk_Assessor` node formulates compliance checks, which are subsequently verified by an independent `Audit_Committee` node before execution routing.

### B. Tooling & Infrastructure (Model Context Protocol)
* **Decoupled Nervous System:** All API tools, SQL databases, and Vector stores are segregated from the reasoning engine via the open-source **Model Context Protocol (MCP)**. 
* **Legacy Mainframe Integration:** SQLite/PostgreSQL ledgers are securely queried via parameterised MCP endpoints, preventing LLMs from direct database write-access.

### C. DevSecAI & Governance
* **Shift-Left Security Gateway:** A dedicated `Security_Officer` node intercepts all ingress traffic, evaluating payloads for prompt injections and roleplay jailbreaks *before* graph execution.
* **Human-in-the-Loop (HITL) Breakpoints:** Execution nodes (`Trade_Executor`) are protected by a graph-level interrupt (`interrupt_before`). The Python process physically suspends state to SQLite, awaiting manual terminal/API `APPROVE` overrides.
* **Eval-Driven Development (CI/CD):** Deployments are gated by a deterministic integration testing pipeline (`run_evals.py`) that strictly enforces semantic role boundaries.

### D. Observability (LangSmith)
* **Zero-Code Telemetry:** Distributed tracing is injected dynamically via environment variables (`LANGCHAIN_TRACING_V2`). 
* **Data Residency:** All telemetry is strictly routed to European infrastructure (`eu.api.smith.langchain.com`) to ensure UK GDPR compliance for financial PII.