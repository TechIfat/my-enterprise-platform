# ADR 008: Distributed Tracing & Observability via LangSmith (EU Data Residency)

## Context
As the Enterprise Agentic Platform (EAP) executes complex, multi-step routing decisions, traditional logging (`stdout`/`print`) is insufficient for debugging hallucinations, tracking API latency, or auditing token costs. Furthermore, because this platform targets the Banking/Fintech sector, any telemetry solution must strictly adhere to UK GDPR and European data residency laws.

## Decision
We implemented LangSmith as our distributed tracing and observability layer, injected dynamically via environment variables without coupling telemetry logic directly into the LangGraph business logic. Crucially, all telemetry is explicitly routed to the LangSmith EU tenant (`eu.api.smith.langchain.com`).

## Reasoning
* **Data Residency & Compliance:** By hardcoding the EU endpoint in our environment configurations, we guarantee that all prompt payloads, LLM responses, and PII processed by the swarm remain within European data centers, satisfying strict banking compliance requirements.
* **Zero-Code Instrumentation:** By leveraging `LANGCHAIN_TRACING_V2`, we achieve full visibility into LLM calls, tool executions, and state transitions without cluttering the Python codebase.
* **Cost & Latency Auditing:** Provides granular metrics on token usage and bottleneck identification (e.g., identifying if the MCP server or the Anthropic API is causing slow responses).
* **Environment Separation:** By dynamically setting `LANGCHAIN_PROJECT` via our Typer CLI environment injector, we securely separate development traces from production telemetry.