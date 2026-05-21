# Models, Messages, and Tools

## Models

Use LangChain chat models inside LangGraph nodes.

Provider-independent initialization:

```python
from langchain.chat_models import init_chat_model


model = init_chat_model("openai:gpt-5-nano", temperature=0)
response = model.invoke("Write one sentence about LangGraph.")
print(response.content)
```

Provider-specific initialization:

```python
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model="gpt-5-nano", temperature=0, timeout=30)
```

Common methods:

- `invoke(input)`: one input.
- `ainvoke(input)`: async one input.
- `stream(input)`: incremental output.
- `batch(inputs)`: many inputs.

When batching model calls, pass runnable config such as `max_concurrency` if you need to cap parallel requests.

## Messages

Messages are the unit of chat context. Use strings for simple one-off calls; use message lists for conversations and LangGraph state.

```python
from langchain.messages import SystemMessage, HumanMessage, AIMessage


messages = [
    SystemMessage(content="You are concise."),
    HumanMessage(content="Explain reducers in LangGraph."),
]

response = model.invoke(messages)
messages.append(response)
```

Dictionary format also works:

```python
messages = [
    {"role": "system", "content": "You are concise."},
    {"role": "user", "content": "Explain reducers in LangGraph."},
]
```

Main message types:

- `SystemMessage`: behavior/context instructions.
- `HumanMessage`: user input.
- `AIMessage`: model output, including tool calls and metadata.
- `ToolMessage`: tool execution result paired with a tool call ID.

## Tools

Tools are callable functions with schemas that a model or agent can choose to call.

```python
from langchain.tools import tool


@tool
def get_account_status(account_id: str) -> str:
    """Return account status for an account ID."""
    return "active"
```

For clearer schemas, use type hints and docstrings. For complex arguments, use Pydantic:

```python
from typing import Literal
from pydantic import BaseModel, Field
from langchain.tools import tool


class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    source: Literal["docs", "tickets"] = "docs"


@tool(args_schema=SearchInput)
def search_knowledge_base(query: str, source: str = "docs") -> str:
    """Search a knowledge base."""
    return f"Results for {query} in {source}"
```

## Bind Tools to a Model

```python
model_with_tools = model.bind_tools([get_account_status])
response = model_with_tools.invoke("Check account A-123.")

for tool_call in response.tool_calls:
    print(tool_call["name"], tool_call["args"], tool_call["id"])
```

In a custom LangGraph tool node, execute tool calls and return `ToolMessage` objects.

```python
from langchain.messages import ToolMessage


tools = [get_account_status]
tools_by_name = {tool.name: tool for tool in tools}


def call_tools(state: State) -> dict:
    results = []
    for call in state["messages"][-1].tool_calls:
        tool = tools_by_name[call["name"]]
        output = tool.invoke(call["args"])
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
    return {"messages": results}
```

## Source Links

- Models: https://docs.langchain.com/oss/python/langchain/models
- Messages: https://docs.langchain.com/oss/python/langchain/messages
- Tools: https://docs.langchain.com/oss/python/langchain/tools
