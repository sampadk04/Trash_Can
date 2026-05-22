# Minimal LangGraph And LangChain Reference

## StateGraph Basics

Use `StateGraph` for custom orchestration:

```python
from langgraph.graph import START, END, StateGraph

builder = StateGraph(MyState)
builder.add_node("node_name", node_fn)
builder.add_edge(START, "node_name")
builder.add_edge("node_name", END)
graph = builder.compile()
result = await graph.ainvoke(initial_state)
```

Nodes read state and return partial updates:

```python
async def request_card(state: CreditCardState) -> dict:
    return {
        "fetch_card_details": "yes",
        "bot_response": "Please select the credit card for payment.",
        "next_action": NextAction(
            intent="PAY_CREDIT_CARD_BILL.SHOW_CREDIT_CARDS",
            intent_type="Clarification",
        ),
    }
```

Prefer returning updates over mutating the input state in place.

## Conditional Edges

Use conditional edges for visible routing:

```python
from typing import Literal

def route_email_update(state: EmailState) -> Literal[
    "request_eligibility",
    "show_not_eligible",
    "request_new_email",
    "raise_confirmation",
    "classify_confirmation",
    "show_final_status",
]:
    if state.status in {"success", "failure"}:
        return "show_final_status"
    if state.eligibility_checked == "no":
        return "request_eligibility"
    if state.is_eligible == "no":
        return "show_not_eligible"
    if not state.new_email:
        return "request_new_email"
    if state.confirmation_raised == "no":
        return "raise_confirmation"
    return "classify_confirmation"

builder.add_conditional_edges("reset_flags", route_email_update)
```

Use a mapping when route labels differ from node names:

```python
builder.add_conditional_edges(
    "classify_confirmation",
    route_after_confirmation,
    {
        "yes": "request_email_mfa",
        "no": "abort_email_update",
        "ambiguous": "ask_confirmation_again",
    },
)
```

## Command

Use `Command` when a node naturally updates state and chooses the next node:

```python
from typing import Literal
from langgraph.types import Command

async def classify_confirmation(
    state: EmailState,
) -> Command[Literal["request_email_mfa", "abort_email_update", "ask_confirmation_again"]]:
    decision = await classifier.ainvoke([...])
    if decision.confirmation == "yes":
        return Command(update={"confirmation": "yes"}, goto="request_email_mfa")
    if decision.confirmation == "no":
        return Command(update={"confirmation": "no"}, goto="abort_email_update")
    return Command(update={"confirmation": "ambiguous"}, goto="ask_confirmation_again")
```

Use this sparingly; conditional edges are easier to inspect for simple routes.

## Runtime Context

Keep request-scoped dependencies out of persisted state. If needed, use LangGraph runtime context for clients/config. For V1 Optimus migrations, passing `journey_data` through input state and excluding it before persistence is acceptable.

## Pydantic Structured Output

Use LangChain structured output for bounded classifiers and extractors:

```python
from typing import Literal
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    next_step: Literal["extract", "abort", "off_topic", "continue"] = Field(
        description=(
            "Bounded route selected from the legacy classifier: 'extract' runs slot extraction, "
            "'abort' ends the journey with an empty app intent, 'off_topic' increments the legacy off-topic counter, "
            "and 'continue' follows the current missing-slot or callback-resume flow."
        )
    )

router = model.with_structured_output(RouteDecision)
decision = await router.ainvoke([
    ("system", "Classify the user's message for this active payment journey."),
    ("human", state.user_query),
])

# Good: store only plain values in graph state.
return {"route": decision.next_step}

# Bad: do not store Pydantic decisions, AIMessage/raw response objects, or parsed wrappers.
# return {"decision": decision}
```

Good uses:

- route selection
- confirmation classification
- slot extraction
- journey-specific off-topic/abort detection

Avoid open-ended agent loops for these handlers.

For migrated legacy prompts, keep the original prompt text and examples as close to verbatim as practical. Pydantic descriptions reinforce the schema; they do not replace the curated prompt rules.

Serialization rule: LangGraph state and node updates should contain plain serializable values. Raw LangChain/OpenAI response objects often contain parsed/tool-call wrapper fields that trigger Pydantic serialization warnings when the graph state is dumped. Extract the fields you need immediately and discard the raw response object.

## ChatOpenAI Factory

Use the repo's shared factory for migrated graph nodes. The current implementation lives at `app/services/optimus_query_bot/langgraph_intent_handlers/utils/llm.py` and uses both sync and async HTTP clients:

```python
from httpx import AsyncClient, Client
from langchain_openai import ChatOpenAI

def build_chat_openai(reasoning_effort: str = "low") -> ChatOpenAI:
    http_client = Client(verify=False)
    async_http_client = AsyncClient(verify=False)
    return ChatOpenAI(
        model="gpt-5.2",
        use_responses_api=True,
        reasoning={"effort": reasoning_effort},
        temperature=None,
        max_retries=2,
        http_client=http_client,
        http_async_client=async_http_client,
    )
```

If the installed `langchain-openai` version changes client keyword names, adapt only the factory and keep node code importing this function. Do not instantiate `ChatOpenAI` directly inside individual usecase nodes.

## Persistence Reminder

LangGraph checkpointers are useful for future replay/debugging, but V1 should keep Redis `StateManager` as the persistence boundary. Run one graph invocation per request turn, then let `LangGraphRuleEngine` save durable state.
