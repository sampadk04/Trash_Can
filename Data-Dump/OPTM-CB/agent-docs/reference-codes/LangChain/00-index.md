# LangChain Docs Pack for LangGraph Systems

Collected on 2026-05-21.

## Scope

This folder contains the minimal LangChain docs needed to design Python LangGraph Graph API systems:

- models,
- messages,
- tools,
- structured outputs,
- reasoning effort,
- `ChatOpenAI`,
- migration from `create_react_agent` to `create_agent`.

## Files

- `models-messages-tools.md`: Minimal primitives to use inside LangGraph nodes.
- `structured-output.md`: Direct model structured outputs and `create_agent` response formats.
- `chatopenai-reasoning.md`: `ChatOpenAI` setup, tools, structured output, Responses API, reasoning.
- `create-agent-migration.md`: How to use `create_agent` instead of `create_react_agent`.

## Source Set

- Models: https://docs.langchain.com/oss/python/langchain/models
- Messages: https://docs.langchain.com/oss/python/langchain/messages
- Tools: https://docs.langchain.com/oss/python/langchain/tools
- Structured output: https://docs.langchain.com/oss/python/langchain/structured-output
- Agents: https://docs.langchain.com/oss/python/langchain/agents
- ChatOpenAI: https://docs.langchain.com/oss/python/integrations/chat/openai
- LangChain v1 migration: https://docs.langchain.com/oss/python/migrate/langchain-v1
- LangGraph v1 migration: https://docs.langchain.com/oss/python/migrate/langgraph-v1
- `chub` IDs fetched:
  - `langchain/package --lang py` version 1.2.11, updated 2026-03-12
  - `langchain/core --lang py` version 1.2.18, updated 2026-03-11
  - `langchain/openai --lang py` version 1.1.11, updated 2026-03-12
