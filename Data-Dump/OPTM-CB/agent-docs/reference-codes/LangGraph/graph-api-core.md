# LangGraph Graph API Core

## Mental Model

LangGraph workflows are graphs with three core parts:

- `State`: shared data snapshot for the run.
- `Nodes`: Python functions that read state and return partial state updates.
- `Edges`: fixed or conditional transitions that decide which node runs next.

Use this as the default architecture for custom workflows. Nodes do work; edges decide movement; state carries facts between steps.

## Basic Graph Shape

```python
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph


class State(TypedDict):
    user_input: str
    answer: str


def answer(state: State) -> dict:
    return {"answer": f"Received: {state['user_input']}"}


builder = StateGraph(State)
builder.add_node("answer", answer)
builder.add_edge(START, "answer")
builder.add_edge("answer", END)

graph = builder.compile()
result = graph.invoke({"user_input": "hello"})
```

## State Schemas

Prefer `TypedDict` for minimal systems:

```python
from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    retrieved_docs: list[str]
    final_answer: str
```

Other supported state schemas include dataclasses and Pydantic models, but keep the default simple unless validation/defaults are worth the extra complexity.

## Partial Updates

Nodes should return partial updates:

```python
def retrieve(state: State) -> dict:
    docs = search(state["question"])
    return {"retrieved_docs": docs}
```

Do not mutate the input state in place. Return only the fields changed by that node.

## Reducers

Without a reducer, a new update overwrites the existing value.

Use a reducer when multiple updates should accumulate:

```python
import operator
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    notes: Annotated[list[str], operator.add]
```

For chat messages, prefer message-aware reducers:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

Or use the prebuilt:

```python
from langgraph.graph import MessagesState


class State(MessagesState):
    retrieved_docs: list[str]
```

## Input, Output, and Private State

For a small graph, one state schema is usually enough. If you want a clean public interface, define separate input/output schemas while keeping richer internal state.

```python
class InputState(TypedDict):
    question: str


class OutputState(TypedDict):
    answer: str


class InternalState(InputState, OutputState):
    search_query: str
    retrieved_docs: list[str]


builder = StateGraph(
    InternalState,
    input_schema=InputState,
    output_schema=OutputState,
)
```

Nodes can write to channels in the graph state even when their input annotation is narrower. Use this carefully; it is useful for hiding internal work from graph consumers.

## Runtime Context

Use runtime context for run-scoped dependencies/config that should not be persisted in graph state:

```python
from dataclasses import dataclass
from langgraph.runtime import Runtime


@dataclass
class Context:
    tenant_id: str


class State(TypedDict):
    question: str
    answer: str


def answer(state: State, runtime: Runtime[Context]) -> dict:
    return {"answer": f"{runtime.context.tenant_id}: {state['question']}"}


builder = StateGraph(State, context_schema=Context)
graph = builder.add_node("answer", answer).add_edge(START, "answer").compile()

graph.invoke({"question": "hi"}, context={"tenant_id": "acme"})
```

Keep API keys, client handles, tenant IDs, and request-scoped dependencies out of persisted state unless they are intentionally part of the business record.

## Normal and Conditional Edges

Normal edge:

```python
builder.add_edge("retrieve", "answer")
```

Conditional edge:

```python
from typing import Literal


def route(state: State) -> Literal["retrieve", "answer"]:
    if state.get("retrieved_docs"):
        return "answer"
    return "retrieve"


builder.add_conditional_edges("classify", route)
```

## Command

Use `Command` when a node needs to update state and choose the next node together:

```python
from typing import Literal
from langgraph.types import Command


def classify(state: State) -> Command[Literal["retrieve", "answer"]]:
    if state["question"].endswith("?"):
        return Command(update={"search_query": state["question"]}, goto="retrieve")
    return Command(update={"answer": "No question detected."}, goto="answer")
```

This keeps routing local to the node that made the decision. It works well for LLM-classification/router nodes.

## Source Links

- Graph API overview: https://docs.langchain.com/oss/python/langgraph/graph-api
- Use the Graph API: https://docs.langchain.com/oss/python/langgraph/use-graph-api
