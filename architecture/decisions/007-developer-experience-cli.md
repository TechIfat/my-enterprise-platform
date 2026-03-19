# ADR 007: Unified Developer Experience via Typer CLI

## Context
As the Enterprise Agentic Platform (EAP) scales, it now includes multiple microservices (FastAPI Gateway, MCP Server), state management systems (SQLite Checkpointers), and vector databases (ChromaDB). Requiring developers to memorize and execute disjointed Python scripts increases onboarding friction and deployment errors.

## Decision
We implemented a unified Command Line Interface (CLI) using `Typer` to encapsulate all platform operations (`seed`, `chat`, `serve`) under a single `eap` global command.

## Reasoning
* **Developer Velocity:** Standardises operations. New engineers only need to learn one command (`eap --help`) to operate the entire ecosystem.
* **Separation of Concerns:** The CLI abstracts away the underlying execution logic (e.g., Uvicorn parameters, subprocess handling).
* **Future CI/CD Integration:** A unified CLI allows CI/CD pipelines (like GitHub Actions) to cleanly execute `eap seed` or `eap test` without knowing the exact file structure of the repository.