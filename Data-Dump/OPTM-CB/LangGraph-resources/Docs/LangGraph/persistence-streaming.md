# Persistence and Streaming

## Persistence: Checkpointers and Threads

Persistence is enabled by compiling a graph with a checkpointer.

```python
from langgraph.checkpoint.memory import InMemorySaver


checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

When a checkpointer is used, pass a `thread_id` in config:

```python
config = {"configurable": {"thread_id": "thread-1"}}

result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hi"}]},
    config=config,
)
```

Use the same `thread_id` to continue the same state lineage.

## What Checkpointing Gives You

Checkpointing supports:

- conversation or workflow continuity across calls,
- pause/resume flows such as human review,
- replay/time-travel style debugging,
- fault tolerance after failures,
- state inspection.

For minimal local development, `InMemorySaver` is fine. For production, use a persistent checkpoint backend.

## Checkpointer vs Store

Use a checkpointer for thread/run state:

- current messages,
- current task progress,
- intermediate node outputs,
- interrupt/resume state.

Use a store for cross-thread memory:

- user preferences,
- shared facts,
- durable app-level memories.

Keep the first implementation checkpoint-only unless you clearly need cross-thread memory.

## Streaming Basics

Compiled graphs support `.stream()` and `.astream()`.

Common stream modes:

- `updates`: node-level state updates.
- `values`: full state snapshots.
- `messages`: model token/message streaming.
- `custom`: custom data emitted from inside nodes.
- `debug`: verbose runtime details.

```python
for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "Summarize this."}]},
    config={"configurable": {"thread_id": "thread-1"}},
    stream_mode="updates",
):
    print(chunk)
```

## v2 Stream Format

For LangGraph versions that support it, use `version="v2"` for consistent stream parts:

```python
for part in graph.stream(
    {"topic": "LangGraph"},
    stream_mode=["updates", "custom"],
    version="v2",
):
    if part["type"] == "updates":
        print(part["data"])
    elif part["type"] == "custom":
        print(part["data"])
```

## Custom Streaming from Nodes

Use custom streaming for progress events that are not graph state.

```python
from langgraph.config import get_stream_writer


def retrieve(state: State) -> dict:
    writer = get_stream_writer()
    writer({"stage": "retrieving"})
    docs = search(state["question"])
    writer({"stage": "retrieved", "count": len(docs)})
    return {"retrieved_docs": docs}
```

Then stream with `stream_mode="custom"` or a list including `custom`.

## Minimal Persistent Agent Loop

```python
from langgraph.checkpoint.memory import InMemorySaver


graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "user-123-session-1"}}

first = graph.invoke(
    {"messages": [{"role": "user", "content": "My name is Ada."}]},
    config=config,
)

second = graph.invoke(
    {"messages": [{"role": "user", "content": "What is my name?"}]},
    config=config,
)
```

The checkpointer ties both calls to the same thread.

## Source Links

- Persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- Streaming: https://docs.langchain.com/oss/python/langgraph/streaming
- Graph API overview: https://docs.langchain.com/oss/python/langgraph/graph-api
