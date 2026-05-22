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

Migrate one use case at a time. For every migration, use this source/target map:

```text
source:
  app/services/optimus_query_bot/intent_handlers/<legacy_handler>.py
  app/services/optimus_query_bot/rule_engine.py

target:
  app/services/optimus_query_bot/langgraph_intent_handlers/usecase_handlers/<usecase_slug>/
    __init__.py
    models.py
    nodes.py
    prompts.py
    graph.py
    handler.py
  app/services/optimus_query_bot/langgraph_rule_engine.py
  app/services/optimus_query_bot/fsm-langgraph-migration-report/<usecase_slug>_migration_analysis.md
```

Keep each use case local: state in `models.py`, node implementations in `nodes.py`, graph assembly in `graph.py`, prompts in `prompts.py`, and the rule-engine adapter in `handler.py`. Use `open-fd-reference-pattern.md` as the portable reference for file responsibilities and naming.

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

## Coding Conventions

Mirror the bundled `OPEN_FD` reference pattern:

- Use lower snake_case usecase folders and files.
- Use Pydantic state classes named after the journey, for example `OpenFDState`.
- Keep structured-output models near the state model in `models.py`.
- Use uppercase prompt constants in `prompts.py`.
- Use private helper functions in `nodes.py` for deterministic domain rules.
- Name graph nodes with the usecase prefix when useful: `merge_fd_inputs`, `reset_fd_flags`, `classify_fd_control`.
- Use async node functions that return partial dictionaries; do not mutate input state in place.
- Add `Literal` route aliases in `graph.py` for route function return values.
- Keep `build_<usecase>_graph()` as the only graph-construction function exported to the handler.
- Keep `handler.py` small: build graph, invoke it, normalize output to the Pydantic state model, resolve `NextAction`, call `durable_state`, return RuleEngine-compatible response.
- Keep action fallback logic in the handler only as a safety net; action nodes should set `next_action` directly.
- Use `durable_state(state, extra_exclusions={...})` for usecase-specific transient exclusions.
- Reuse shared `BaseJourneyState`, `NextAction`, `build_chat_openai`, and `durable_state` instead of redefining them in each use case.

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

Use the repo's shared `build_chat_openai` factory from `langgraph_intent_handlers/utils/llm.py`. Do not construct `ChatOpenAI` directly inside usecase nodes. Keep low reasoning effort for bounded classifiers and extractors unless a specific parity issue requires more.

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
    "OPEN_FD": OpenFDGraphHandler,
    # Add one handler at a time after migration review.
}
```

Do not enable an intent globally until parity tests pass. Disabled or unknown graph intents should fall back to FSM through selector/config, not fail production traffic.

## Reference Pattern And Rollout

`OPEN_FD` informed this skill's reference pattern. Do not depend on live migrated `OPEN_FD` files as source material; use the bundled `open-fd-reference-pattern.md` instead.

For remaining handlers, continue one use case at a time. A practical order is:

```text
1. LOAN_NOC
2. PAY_CREDIT_CARD_BILL
3. EMAIL_UPDATE
4. MOBILE_UPDATE
5. PAY_TO_MOBILE
```

`OPEN_FD` was the richest slot-filling migration; use it for conventions, not as proof that simpler backend/widget flows should copy its exact graph shape.

## Migration Analysis Report

Create a report for every migrated use case:

```text
app/services/optimus_query_bot/fsm-langgraph-migration-report/<usecase_slug>_migration_analysis.md
```

Keep it minimal and high-level, but include enough concrete comparison to catch missed functionality:

```markdown
# <INTENT> FSM To LangGraph Migration Analysis

## Scope

- Source FSM:
- Target LangGraph:
- Contract references:

## Overall Finding

One short paragraph on whether the graph preserves the FSM's core flow.

## Source To Target Map

| Component | FSM Source | LangGraph Target | Notes |
| --- | --- | --- | --- |

## Parity Matrix

| Area | FSM Behavior | LangGraph Behavior | Parity |
| --- | --- | --- | --- |

## State Variable Flow

| State Field | FSM Role | LangGraph Role | Durable? | Notes |
| --- | --- | --- | --- | --- |

## Prompt And Classifier Parity

| LLM Helper | FSM Prompt/Schema | LangGraph Model/Prompt | Risk |
| --- | --- | --- | --- |

## App Contract Parity

| App Intent/Response | FSM | LangGraph | Parity |
| --- | --- | --- | --- |

## Coding Convention Check

Brief notes on file structure, node naming, transient exclusions, and registry/fallback.

## Remaining Risks

Short bullets only.

## Suggested Parity Scenarios

| Scenario | Input/State | Expected App Intent |
| --- | --- | --- |
```

Use this template directly for future reports.

## Acceptance Checklist

A handler migration is complete when:

- FSM handler still exists and remains callable.
- Graph handler has Pydantic state, nodes, graph builder, and adapter.
- Graph exposes the same app-facing intents as the FSM.
- Durable state keys are compatible with the FSM or mid-journey switching is explicitly prevented.
- Migration analysis report exists with a parity matrix and residual risks.
- Tests prove first turn, callback resume, abort, status/failure, and final confirmation cases.
- Registry/feature flag can turn the graph handler off without code rollback.
