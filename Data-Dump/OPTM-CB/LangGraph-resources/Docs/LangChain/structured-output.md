# Structured Outputs

Use structured output when a graph node needs reliable machine-readable decisions, classifications, plans, or extraction results.

## Direct Model Structured Output

Best for LangGraph router/classifier nodes:

```python
from typing import Literal
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    next_step: Literal["retrieve", "answer", "human_review"] = Field(
        description="The next LangGraph node to execute."
    )
    reason: str = Field(description="Brief reason for the route.")


router = model.with_structured_output(RouteDecision)

decision = router.invoke("User asks for a policy-backed answer.")
print(decision.next_step)
```

Use this result to update graph state:

```python
def classify(state: State) -> dict:
    decision = router.invoke(state["request"])
    return {
        "route": decision.next_step,
        "route_reason": decision.reason,
    }
```

## Agent Structured Output with `create_agent`

When using the prebuilt LangChain agent loop, pass `response_format`.

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent


class ContactInfo(BaseModel):
    name: str = Field(description="Person name")
    email: str = Field(description="Email address")


agent = create_agent(
    model="openai:gpt-5-nano",
    tools=[],
    response_format=ContactInfo,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Jane, jane@example.com"}]}
)
print(result["structured_response"])
```

LangChain chooses a provider-native strategy when the model supports it and a tool-calling strategy otherwise. You can also explicitly use `ProviderStrategy` or `ToolStrategy`.

## Where to Use in LangGraph

Good uses:

- route selection,
- query rewriting,
- document relevance grading,
- output quality/evaluation,
- planner output,
- extraction from documents.

Avoid using structured output only to force a final natural language answer into JSON when a plain `AIMessage` is enough.

## Minimal Router Example

```python
from typing import Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END


class Route(BaseModel):
    step: Literal["search", "final"]


router = model.with_structured_output(Route)


class State(TypedDict):
    input: str
    route: str
    answer: str


def decide(state: State) -> dict:
    route = router.invoke(state["input"])
    return {"route": route.step}


def route_next(state: State) -> Literal["search", "final"]:
    return state["route"]
```

## Source Links

- Structured output: https://docs.langchain.com/oss/python/langchain/structured-output
- ChatOpenAI structured output: https://docs.langchain.com/oss/python/integrations/chat/openai
- Agents: https://docs.langchain.com/oss/python/langchain/agents
