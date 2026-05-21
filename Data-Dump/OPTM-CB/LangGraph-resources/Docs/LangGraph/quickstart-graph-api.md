# LangGraph Quickstart: Graph API Only

Use this pattern when you want a small ReAct-style loop but still want to see and control the graph nodes/edges yourself.

## Install

```bash
pip install -U langgraph langchain langchain-openai
```

## Minimal Tool-Calling Graph

```python
import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


tools = [add, multiply]
tools_by_name = {tool.name: tool for tool in tools}

model = ChatOpenAI(model="gpt-5-nano", temperature=0)
model_with_tools = model.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def call_model(state: State) -> dict:
    response = model_with_tools.invoke(
        [
            SystemMessage(
                content="You are a careful assistant. Use tools for arithmetic."
            )
        ]
        + state["messages"]
    )
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def call_tools(state: State) -> dict:
    tool_messages = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        output = tool.invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(content=str(output), tool_call_id=tool_call["id"])
        )
    return {"messages": tool_messages}


def should_continue(state: State) -> Literal["call_tools", "__end__"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tools"
    return END


builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_node("call_tools", call_tools)
builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", should_continue)
builder.add_edge("call_tools", "call_model")

graph = builder.compile()

result = graph.invoke(
    {"messages": [HumanMessage(content="Add 3 and 4, then multiply by 2.")]}
)
print(result["messages"][-1].content)
```

## Notes

- The official quickstart shows the same shape: define tools/model, define message state, define an LLM node, define a tool node, route with a conditional edge, then compile.
- `StateGraph` is only the builder. Always call `.compile()` before invoking or streaming.
- The quickstart uses `operator.add` for messages. For production chat state, prefer `langgraph.graph.message.add_messages` or `MessagesState` when you need message ID-aware updates.

## Source Links

- Official quickstart: https://docs.langchain.com/oss/python/langgraph/quickstart
- Graph API overview: https://docs.langchain.com/oss/python/langgraph/graph-api
