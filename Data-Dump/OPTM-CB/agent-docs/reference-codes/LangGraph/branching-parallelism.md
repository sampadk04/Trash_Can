# Branching, Conditional Branching, and Parallelism

## Fixed Branching

Multiple outgoing normal edges from one node create parallel work in the next super-step.

```python
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph


class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined: str


def write_joke(state: State) -> dict:
    return {"joke": f"Joke about {state['topic']}"}


def write_story(state: State) -> dict:
    return {"story": f"Story about {state['topic']}"}


def write_poem(state: State) -> dict:
    return {"poem": f"Poem about {state['topic']}"}


def combine(state: State) -> dict:
    return {"combined": "\n\n".join([state["story"], state["joke"], state["poem"]])}


builder = StateGraph(State)
builder.add_node("write_joke", write_joke)
builder.add_node("write_story", write_story)
builder.add_node("write_poem", write_poem)
builder.add_node("combine", combine)
builder.add_edge(START, "write_joke")
builder.add_edge(START, "write_story")
builder.add_edge(START, "write_poem")
builder.add_edge("write_joke", "combine")
builder.add_edge("write_story", "combine")
builder.add_edge("write_poem", "combine")
builder.add_edge("combine", END)
graph = builder.compile()
```

Use this for independent tasks with known fan-out.

## Conditional Branching

Use conditional edges when the next node depends on current state.

```python
from typing import Literal


class State(TypedDict):
    request: str
    route: Literal["retrieve", "answer", "human_review"] | None
    answer: str


def classify(state: State) -> dict:
    if "urgent" in state["request"].lower():
        return {"route": "human_review"}
    if "docs" in state["request"].lower():
        return {"route": "retrieve"}
    return {"route": "answer"}


def route_after_classify(
    state: State,
) -> Literal["retrieve", "answer", "human_review"]:
    return state["route"]


builder.add_node("classify", classify)
builder.add_conditional_edges("classify", route_after_classify)
```

Use an explicit mapping when you want return values to differ from node names:

```python
builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "retrieve": "retrieve",
        "answer": "answer",
        "human_review": "human_review",
    },
)
```

## LLM Router Pattern

Use structured output to make routing deterministic enough for graph logic.

```python
from typing import Literal
from pydantic import BaseModel, Field
from langchain.messages import HumanMessage, SystemMessage


class Route(BaseModel):
    next_step: Literal["retrieve", "answer", "human_review"] = Field(
        description="The next graph node to execute."
    )


router = model.with_structured_output(Route)


def classify(state: State) -> dict:
    decision = router.invoke(
        [
            SystemMessage(content="Choose the next workflow step."),
            HumanMessage(content=state["request"]),
        ]
    )
    return {"route": decision.next_step}
```

## Conditional Parallel Branching

A routing function can return multiple destinations:

```python
from collections.abc import Sequence


def route_research(state: State) -> Sequence[str]:
    if state["route"] == "full_review":
        return ["retrieve_policy", "retrieve_history", "retrieve_examples"]
    return ["retrieve_policy"]
```

Each destination node can run in the same super-step. Use reducers for keys they update in common.

## Map-Reduce with Send

Use `Send` when you want dynamic fan-out with worker-specific state.

```python
import operator
from typing import Annotated
from langgraph.types import Send


class State(TypedDict):
    topic: str
    sections: list[str]
    section_notes: Annotated[list[str], operator.add]
    report: str


class WorkerState(TypedDict):
    topic: str
    section: str


def plan_sections(state: State) -> dict:
    return {"sections": ["risks", "benefits", "implementation"]}


def route_workers(state: State) -> list[Send]:
    return [
        Send("write_section_note", {"topic": state["topic"], "section": section})
        for section in state["sections"]
    ]


def write_section_note(state: WorkerState) -> dict:
    return {"section_notes": [f"{state['section']} notes for {state['topic']}"]}


def reduce_report(state: State) -> dict:
    return {"report": "\n".join(state["section_notes"])}


builder = StateGraph(State)
builder.add_node("plan_sections", plan_sections)
builder.add_node("write_section_note", write_section_note)
builder.add_node("reduce_report", reduce_report)
builder.add_edge(START, "plan_sections")
builder.add_conditional_edges("plan_sections", route_workers)
builder.add_edge("write_section_note", "reduce_report")
builder.add_edge("reduce_report", END)
graph = builder.compile()
```

Use this for orchestrator-worker systems: one node decides the work items; worker nodes process each item; a reducer node combines results.

## Pattern Mapping from Local Article

From `Workflows-and-Agents.md`:

- Prompt chaining: sequential nodes with validation gates.
- Routing: LLM structured output or code-based classification plus conditional edges.
- Parallelization: multiple independent nodes plus an aggregator.
- Orchestrator-worker: dynamic decomposition with `Send` and a reducer channel.
- Evaluator-optimizer: a loop where an evaluator routes back for improvement or forward to `END`.

## Source Links

- Use the Graph API: https://docs.langchain.com/oss/python/langgraph/use-graph-api
- Workflows and agents: https://docs.langchain.com/oss/python/langgraph/workflows-agents
