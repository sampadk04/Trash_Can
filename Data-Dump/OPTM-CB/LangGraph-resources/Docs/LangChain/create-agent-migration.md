# Migration: Use `create_agent`, Not `create_react_agent`

## Current Rule

For a prebuilt vanilla agent loop, use:

```python
from langchain.agents import create_agent
```

Do not start new code with:

```python
from langgraph.prebuilt import create_react_agent
```

Official migration docs state that LangGraph v1 deprecates `create_react_agent` in favor of LangChain's `create_agent`.

## Basic `create_agent`

```python
from langchain.agents import create_agent


def search_docs(query: str) -> str:
    """Search internal docs."""
    return "stub result"


agent = create_agent(
    model="openai:gpt-5-nano",
    tools=[search_docs],
    system_prompt="You answer using tools when needed.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Find the refund policy."}]}
)

print(result["messages"][-1].content)
```

`create_agent` builds a graph-based agent runtime on LangGraph. Use it when the default model/tools loop is enough.

## Important Migration Changes

- Import path changed from `langgraph.prebuilt` to `langchain.agents`.
- Function name changed from `create_react_agent` to `create_agent`.
- `prompt` became `system_prompt`.
- Custom state for `create_agent` should be `TypedDict`-based.
- Dynamic model selection and hooks now use middleware.
- Pre-bound models with tools are not the default path; pass tools to `create_agent`.
- Structured output should use `response_format` with provider/tool strategies.
- Streaming node naming changed in migration notes from old `"agent"` naming to model-oriented naming.

## When to Use `create_agent`

Use it for:

- straightforward tool-using assistants,
- a standard model -> tools -> model loop,
- quick prototypes,
- cases where middleware is enough customization.

## When to Use LangGraph Graph API Directly

Use `StateGraph` when you need:

- custom branching,
- multiple specialized LLM nodes,
- explicit retrieval/generation/evaluation phases,
- human review nodes,
- dynamic orchestrator-worker patterns,
- custom state schemas,
- durable workflow control beyond a vanilla agent loop.

## `create_agent` with ChatOpenAI

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


model = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0,
    reasoning={"effort": "low", "summary": "auto"},
)

agent = create_agent(
    model=model,
    tools=[],
    system_prompt="You are concise.",
)
```

## `create_agent` with Structured Response

```python
from pydantic import BaseModel
from langchain.agents import create_agent


class Answer(BaseModel):
    answer: str
    confidence: float


agent = create_agent(
    model="openai:gpt-5-nano",
    tools=[],
    response_format=Answer,
)
```

The final state includes `structured_response`.

## Source Links

- LangChain v1 migration guide: https://docs.langchain.com/oss/python/migrate/langchain-v1
- LangGraph v1 migration guide: https://docs.langchain.com/oss/python/migrate/langgraph-v1
- Agents: https://docs.langchain.com/oss/python/langchain/agents
