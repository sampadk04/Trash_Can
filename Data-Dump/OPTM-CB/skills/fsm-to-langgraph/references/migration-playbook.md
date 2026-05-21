# Migration Playbook

## Target Layout

Use a parallel architecture:

```text
app/services/optimus_query_bot/
  rule_engine.py
  intent_handlers/

  langgraph_rule_engine.py
  langgraph_intent_handlers/
    __init__.py
    models/
      __init__.py
      base.py
      actions.py
    utils/
      __init__.py
      adapters.py
      llm.py
      state.py
      validators.py
    usecase_handlers/
      __init__.py
      loan_noc/
        __init__.py
        models.py
        nodes.py
        graph.py
        prompts.py
        handler.py
```

Keep each use case local: state in `models.py`, node implementations in `nodes.py`, graph assembly in `graph.py`, prompts in `prompts.py`, and the rule-engine adapter in `handler.py`.

## Shared Models

Use Pydantic models for V1 graph state because defaults, field descriptions, and permissive legacy compatibility matter.

```python
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

YesNo = Literal["yes", "no"]


class NextAction(BaseModel):
    intent: str = Field(description="App-facing intent name to return for this turn.")
    intent_type: str = Field(description="Clarification, Execution, Redirection, or legacy-compatible value.")
    additional_data: dict[str, Any] = Field(default_factory=dict)


class BaseJourneyState(BaseModel):
    model_config = ConfigDict(extra="allow")

    journey: str = Field(description="Journey identifier.")
    user_query: str = ""
    bot_response: str = ""
    abort: YesNo = "no"
    off_topic_count: int = 0
    widget_response: YesNo = "no"
    next_action: NextAction | None = None
```

Use handler-specific fields with the same durable names as the FSM where possible.

## Shared Node Types

Every handler usually needs:

```text
merge_inputs
  Load persisted state, merge allowed callback fields, attach user_query, normalize yes/no strings.

reset_turn_flags
  Clear one-turn flags and next_action at the beginning of each turn.

classify_control
  Optional bounded structured-output classifier for abort/change/off-topic/confirmation.

extract_slot
  Optional structured-output extractor for FD or UPI slots.

validate_domain_rule
  Deterministic validation for amounts, tenure plans, callback completeness, and balances.

emit_action
  Set bot_response, one-turn legacy flags if retained, and next_action.
```

Prefer one node per business step. Avoid giant "do everything" nodes that recreate the FSM.

## Graph Pattern

```python
from typing import Literal
from langgraph.graph import START, END, StateGraph


def route_next(state: SomeState) -> Literal["request_slot", "prepare_confirmation", "show_final_status"]:
    ...


def build_graph():
    builder = StateGraph(SomeState)
    builder.add_node("merge_inputs", merge_inputs)
    builder.add_node("reset_flags", reset_flags)
    builder.add_node("request_slot", request_slot)
    builder.add_node("prepare_confirmation", prepare_confirmation)
    builder.add_node("show_final_status", show_final_status)

    builder.add_edge(START, "merge_inputs")
    builder.add_edge("merge_inputs", "reset_flags")
    builder.add_conditional_edges("reset_flags", route_next)

    for terminal_node in ["request_slot", "prepare_confirmation", "show_final_status"]:
        builder.add_edge(terminal_node, END)

    return builder.compile()
```

Use conditional edges for visible routing. Use `Command` for classifier nodes that both set state and decide the next node.

## LLM Pattern

Migrate JSON-schema gateway helpers to Pydantic structured output:

```python
from typing import Literal
from pydantic import BaseModel, Field


class EmailConfirmation(BaseModel):
    confirmation: Literal["yes", "no", "ambiguous"] = Field(
        description="Whether the user confirms, rejects, or gives an unclear response."
    )


async def classify_email_confirmation(state: EmailState) -> dict:
    llm = build_chat_openai(reasoning_effort="low")
    classifier = llm.with_structured_output(EmailConfirmation)
    decision = await classifier.ainvoke([
        ("system", EMAIL_CONFIRMATION_PROMPT),
        ("human", state.user_query),
    ])
    return {"confirmation": decision.confirmation}
```

Create a shared `build_chat_openai` factory. The migration guide recommends `ChatOpenAI(model="gpt-5.4", use_responses_api=True, reasoning={"effort": "low"}, temperature=None, max_retries=2, ...)`; adapt only the client argument name if the installed `langchain-openai` version differs.

## Rule Engine Adapter

Add `LangGraphRuleEngine` beside `RuleEngine`. It should:

- keep `validate_journey_data` equivalent
- load `journey_state` via `StateManager`
- call the graph handler's `process(...)`
- save durable state minus response/transient fields
- return the same response shape as `RuleEngine`

Use an incremental registry:

```python
GRAPH_HANDLER_REGISTRY = {
    "LOAN_NOC": LoanNocGraphHandler,
}
```

Do not enable an intent globally until parity tests pass. Disabled or unknown graph intents should fall back to FSM through selector/config, not fail production traffic.

## Rollout Order

Recommended migration order:

```text
1. LOAN_NOC
2. PAY_CREDIT_CARD_BILL
3. EMAIL_UPDATE
4. MOBILE_UPDATE
5. PAY_TO_MOBILE
6. OPEN_FD
```

`OPEN_FD` is last because bare-number disambiguation, plan selection, and change-intent handling make it the richest flow.

## Acceptance Checklist

A handler migration is complete when:

- FSM handler still exists and remains callable.
- Graph handler has Pydantic state, nodes, graph builder, and adapter.
- Graph exposes the same app-facing intents as the FSM.
- Durable state keys are compatible with the FSM or mid-journey switching is explicitly prevented.
- Tests prove first turn, callback resume, abort, status/failure, and final confirmation cases.
- Registry/feature flag can turn the graph handler off without code rollback.
