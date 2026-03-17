# ADR 005: Decoupled RAG via Model Context Protocol

## Context
Agents require access to proprietary enterprise knowledge (policies, guidelines) to make compliant decisions. Traditional RAG (Retrieval-Augmented Generation) implementations tightly couple the Vector Database connection directly to the LLM orchestration code, creating security risks and deployment bottlenecks.

## Decision
We will host the Vector Database (ChromaDB) behind the Model Context Protocol (MCP) server, exposing it as a standard, restricted tool (`search_internal_knowledge_base`) rather than giving the orchestration layer direct database access.

## Reasoning
* **Separation of Concerns:** Data Engineering teams can update, chunk, and embed documents in ChromaDB independently of the AI Engineering team managing the LangGraph orchestration.
* **Security & Blast Radius:** If an LLM suffers a prompt injection attack, it cannot execute arbitrary queries or drop the database. It is restricted to the strict inputs defined by the MCP tool schema.
* **Microservices Scalability:** The Vector Database and the LLM runtime can be scaled horizontally on completely different cloud infrastructure.