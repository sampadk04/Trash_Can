# State and Worker State Management

## State Design Principles

From the local `Thinking-in-LangGraphs.md` article:

- Start with the process, then turn each distinct step into a node.
- Put data in state when later nodes need it or when it is expensive/impossible to recompute.
- Keep state raw. Format prompts inside nodes.
- Store durable facts and outputs, not prompt templates.

Good state:

```python
from typing_extensions import TypedDict


class SupportState(TypedDict):
    email_content: str
    sender_email: str
    classification: dict | None
    search_results: list[str]
    draft_response: str | None
    final_response: str | None
```

Less useful state:

```python
class SupportState(TypedDict):
    full_prompt_for_classifier: str
    full_prompt_for_response_writer: str
```

Prompts change often and can be rebuilt from raw state.

## Shared State vs Worker State

Use shared graph state for data that must survive between nodes:

- user input
- model decisions
- retrieval results
- generated drafts
- validation results
- final answer

Use worker/local state inside node functions for temporary details:

- prompt strings
- intermediate filtering variables
- client return objects you immediately normalize
- model-specific scratch values

```python
def retrieve(state: SupportState) -> dict:
    query = build_query(state["classification"], state["email_content"])
    raw_docs = search_index(query)
    normalized_docs = [doc.page_content for doc in raw_docs]
    return {"search_results": normalized_docs}
```

Only `normalized_docs` is returned to shared state.

## Private State Channels

If intermediate data is useful between internal nodes but should not be part of graph input/output, define private/internal channels.

```python
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph


class InputState(TypedDict):
    user_request: str


class OutputState(TypedDict):
    final_answer: str


class InternalState(InputState, OutputState):
    route: str
    retrieved_docs: list[str]


def classify(state: InputState) -> dict:
    return {"route": "retrieve"}


def retrieve(state: InternalState) -> dict:
    return {"retrieved_docs": ["doc chunk"]}


def answer(state: InternalState) -> dict:
    return {"final_answer": "\n".join(state["retrieved_docs"])}


builder = StateGraph(
    InternalState,
    input_schema=InputState,
    output_schema=OutputState,
)
builder.add_node("classify", classify)
builder.add_node("retrieve", retrieve)
builder.add_node("answer", answer)
builder.add_edge(START, "classify")
builder.add_edge("classify", "retrieve")
builder.add_edge("retrieve", "answer")
builder.add_edge("answer", END)

graph = builder.compile()
```

The caller sees only `user_request` input and `final_answer` output.

## Message State

For chat or agent loops, use message state:

```python
from langgraph.graph import MessagesState


class State(MessagesState):
    route: str | None
    retrieved_docs: list[str]
```

`MessagesState` gives you a `messages` key with a message-aware reducer, which is safer than blindly appending lists when you may update existing message IDs.

## Parallel Writes

If multiple parallel nodes update the same key, define a reducer.

```python
import operator
from typing import Annotated


class ResearchState(TypedDict):
    topic: str
    findings: Annotated[list[str], operator.add]
```

Each worker can return:

```python
return {"findings": ["one finding"]}
```

The graph will combine those findings instead of treating the concurrent writes as a conflict.

## Practical Rule

Use one state schema first. Split into input/output/private schemas only when:

- you need a stable public graph interface,
- you are hiding internal working channels,
- you want cleaner graph outputs for downstream code,
- or parallel worker nodes need a dedicated merge channel.

## Source Links

- Graph API overview: https://docs.langchain.com/oss/python/langgraph/graph-api
- Use the Graph API: https://docs.langchain.com/oss/python/langgraph/use-graph-api
- Local article: `LangGraph-resources/Articles/Thinking-in-LangGraphs.md`
