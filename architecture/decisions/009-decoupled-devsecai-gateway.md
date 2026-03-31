# ADR 009: Decoupled DevSecAI Gateway (Shift-Left Security)

## Context
As the Enterprise Agentic Platform (EAP) matures, embedding security heuristics (prompt injection detection, PII scrubbing) directly within the LangGraph orchestration file (`agent.py`) creates a dangerous tight-coupling between the AI Engineering team and the DevSecOps team. Furthermore, relying solely on LLMs for prompt injection defense is computationally expensive and vulnerable to sophisticated, PhD-level adversarial attacks.

## Decision
We decoupled the security logic into an independent, extensible module (`src/eap/security/firewall.py`), architecting a "Security Gateway" that intercepts user input *before* it reaches the LangGraph state machine.

## Reasoning
* **Separation of Duties:** The DevSecOps team can now independently update threat models, deploy scheduled ML anomaly-detection models (e.g., DeBERTa for zero-day injections), and manage PII scrubbing (e.g., Microsoft Presidio) without altering the core multi-agent orchestration logic.
* **Defense in Depth:** The architecture supports a multi-layered defense strategy. Fast, deterministic ML models can catch known adversarial vectors instantly, falling back to an LLM semantic check only for complex roleplay jailbreaks.
* **Cost & Compute Optimisation:** By blocking malicious payloads at the Gateway layer, we prevent the costly multi-agent swarm from executing and burning API tokens on unauthorised compute.