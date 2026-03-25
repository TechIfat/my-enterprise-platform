# ADR 011: Cost Optimisation via Semantic Triage Routing

## Context
As user adoption scales, the platform receives a high volume of conversational "chatter" (greetings, acknowledgments). Waking up the primary orchestration engine (Claude 4.6 Sonnet) for these queries incurs unnecessary latency and API token costs. 

## Decision
We implemented an "Edge-Cloud" Semantic Triage pattern. A low-latency, low-cost model (`claude-3-haiku`) sits behind the Security Firewall to evaluate prompt complexity. 

## Reasoning
* **FinOps / Cost Control:** Haiku handles generic conversational tasks at ~1/12th the cost of Sonnet, preserving the expensive model strictly for high-value financial reasoning and multi-tool orchestration.
* **Latency Reduction:** Simple queries are resolved and returned to the user via a direct `Fast_Response` node, bypassing the heavier LangGraph Supervisor loop entirely.
* **Seamless Handoff:** Because LangGraph maintains a unified `State`, if a user transitions from casual chat to a complex financial request in the same session, Triage seamlessly hands the conversation context over to the Supervisor.