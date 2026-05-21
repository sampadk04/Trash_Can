# ChatOpenAI and Reasoning Effort

## Install and Setup

```bash
pip install -U langchain-openai
export OPENAI_API_KEY="..."
```

```python
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0,
    timeout=30,
    max_retries=2,
)
```

Use this class directly inside LangGraph nodes when you want OpenAI-specific configuration.

## Basic Invocation

```python
response = llm.invoke("Explain LangGraph in one sentence.")
print(response.content)
```

Message input:

```python
response = llm.invoke(
    [
        ("system", "You are concise."),
        ("human", "What is a LangGraph reducer?"),
    ]
)
```

## Tool Calling

```python
from langchain.tools import tool


@tool
def lookup_policy(topic: str) -> str:
    """Look up a policy by topic."""
    return f"Policy for {topic}"


llm_with_tools = llm.bind_tools([lookup_policy])
response = llm_with_tools.invoke("Find the refund policy.")
print(response.tool_calls)
```

## Structured Output

```python
from pydantic import BaseModel, Field


class Classification(BaseModel):
    intent: str = Field(description="User intent")
    urgency: str = Field(description="low, medium, high, or critical")


classifier = llm.with_structured_output(Classification)
classification = classifier.invoke("I was charged twice!")
```

For OpenAI native structured output, official docs show `method="json_schema"` on `with_structured_output` for individual model calls when you want the provider-native JSON schema path.

## Responses API

`ChatOpenAI` can use OpenAI's Responses API when Responses-specific features are requested. You can force it:

```python
llm = ChatOpenAI(model="gpt-5-nano", use_responses_api=True)
```

For conversation state, you can manage history through LangGraph state as usual, or use `previous_response_id` for Responses API continuation when that style fits your app.

## Reasoning Effort

For reasoning-capable OpenAI models, pass `reasoning`.

```python
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="gpt-5-nano",
    reasoning={
        "effort": "medium",
        "summary": "auto",
    },
)

response = llm.invoke("What is 3^3?")
print(response.text)
```

The official ChatOpenAI docs describe reasoning summaries as summaries, not raw hidden reasoning. Setting `reasoning` routes through the Responses API.

## Practical Guidance for LangGraph

- Use lower reasoning effort for router/classifier nodes unless mistakes are expensive.
- Use higher reasoning effort for planner/evaluator nodes.
- Keep `temperature=0` for routing and structured output.
- Store reasoning summaries only if they are useful for audit/debugging.
- Do not put provider credentials in graph state.

## Source Links

- ChatOpenAI integration: https://docs.langchain.com/oss/python/integrations/chat/openai
- Models: https://docs.langchain.com/oss/python/langchain/models
- OpenAI package guide from `chub`: `langchain/openai --lang py`
