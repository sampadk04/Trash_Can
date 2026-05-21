# LangGraph Docs Pack

Collected on 2026-05-21 for a minimal Python LangGraph Graph API system.

## Scope

This pack intentionally focuses on:

- Graph API only: `StateGraph`, state schemas, nodes, edges, conditional edges, `Send`, `Command`, compile/invoke/stream.
- Basic LangChain model/tool/message pieces needed inside graph nodes.
- Persistence, streaming, and state design needed for practical agent/workflow systems.
- Design patterns from `LangGraph-resources/Articles/Workflows-and-Agents.md` and `LangGraph-resources/Articles/Thinking-in-LangGraphs.md`.

This pack intentionally excludes:

- Functional API examples and imports such as `langgraph.func.entrypoint` and `task`.
- Deployment, Studio, subgraphs, long-term memory, and advanced production platform docs unless directly relevant to minimal persistence/streaming.

## Files

- `quickstart-graph-api.md`: Minimal tool-calling agent loop with Graph API.
- `graph-api-core.md`: State, nodes, edges, reducers, runtime context, compilation.
- `state-worker-state.md`: How to design shared graph state and per-worker/private state.
- `branching-parallelism.md`: Conditional edges, fan-out/fan-in, and `Send`.
- `persistence-streaming.md`: Checkpointers, threads, `stream()` modes, and custom streaming.
- `design-notes.md`: Practical design guidance derived from the local articles.

## Source Set

- Official LangGraph overview: https://docs.langchain.com/oss/python/langgraph
- Official LangGraph quickstart: https://docs.langchain.com/oss/python/langgraph/quickstart
- Official Graph API overview: https://docs.langchain.com/oss/python/langgraph/graph-api
- Official Use the Graph API guide: https://docs.langchain.com/oss/python/langgraph/use-graph-api
- Official persistence docs: https://docs.langchain.com/oss/python/langgraph/persistence
- Official streaming docs: https://docs.langchain.com/oss/python/langgraph/streaming
- Official LangGraph v1 migration guide: https://docs.langchain.com/oss/python/migrate/langgraph-v1
- Local design articles:
  - `LangGraph-resources/Articles/Workflows-and-Agents.md`
  - `LangGraph-resources/Articles/Thinking-in-LangGraphs.md`
  - `LangGraph-resources/Articles/Graph-API/Graph-API-Overview.md`
  - `LangGraph-resources/Articles/Graph-API/Use-the-Graph-API.md`
- `chub` IDs fetched:
  - `langgraph/package --lang py` version 1.1.0, updated 2026-03-11

## Version Notes

- The `chub` package guide reports `langgraph` Python package docs for version `1.1.0`.
- Official docs note that LangGraph v1 deprecates `langgraph.prebuilt.create_react_agent`; use `langchain.agents.create_agent` when you want a prebuilt vanilla agent loop.
- For custom orchestration, use Graph API with `StateGraph`.
