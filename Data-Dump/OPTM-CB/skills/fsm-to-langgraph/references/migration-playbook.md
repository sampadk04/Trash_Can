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
    intent: str = Field(
        description="Exact app-facing intent name returned for this turn, e.g. PAY_TO_MOBILE.SHOW_CONTACT_LIST or empty string for legacy abort."
    )
    intent_type: str = Field(
        description="Exact app-facing intent_type returned for this turn: Clarification, Execution, Redirection, or empty string for legacy abort."
    )
    additional_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific payload merged into response additional_data, such as payee_name or amount_to_be_paid.",
    )


class BaseJourneyState(BaseModel):
    model_config = ConfigDict(extra="allow")

    journey: str = Field(description="Legacy journey identifier used for persistence and default app intent mapping.")
    user_query: str = Field(default="", description="Latest user utterance for this graph turn; transient and not persisted.")
    bot_response: str = Field(default="", description="Customer-facing response for this turn; excluded from persisted journey state.")
    abort: YesNo = Field(default="no", description="Legacy abort flag. Use 'yes' only when the active journey should terminate.")
    off_topic_count: int = Field(default=0, description="Number of off-topic turns seen in this active journey; preserve legacy threshold behavior.")
    widget_response: YesNo = Field(default="no", description="Whether this turn resumed from an app widget callback; durable only if the legacy FSM saved it.")
    next_action: NextAction | None = Field(default=None, description="Normalized app action selected by the graph; adapter converts this to intent_list and excludes it from persistence.")
```

Use handler-specific fields with the same durable names as the FSM where possible. Every routing, classifier, extractor, app-action, persistence, or validation field must have a useful `Field(description=...)`. The description should include exact enum values and downstream meaning, for example which graph route consumes `control_intent`, what `expected_slot` disambiguates, or which app action a one-turn flag emits.

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
- Use uppercase prompt constants in `prompts.py`, with names that map one-to-one to legacy LLM helper names.
- Use private helper functions in `nodes.py` for deterministic domain rules.
- Name graph nodes with the usecase prefix when useful: `merge_fd_inputs`, `reset_fd_flags`, `classify_fd_control`.
- Use async node functions that return partial dictionaries; do not mutate input state in place.
- Add `Literal` route aliases in `graph.py` for route function return values.
- Keep `build_<usecase>_graph()` as the only graph-construction function exported to the handler.
- Keep `handler.py` small: build graph, invoke it, normalize output to the Pydantic state model, resolve `NextAction`, call `durable_state`, return RuleEngine-compatible response.
- Keep action fallback logic in the handler only as a safety net; action nodes should set `next_action` directly.
- Use `durable_state(state, extra_exclusions={...})` for usecase-specific transient exclusions.
- Reuse shared `BaseJourneyState`, `NextAction`, `build_chat_openai`, and `durable_state` instead of redefining them in each use case.
- Make Pydantic `Field` descriptions rich enough for a reviewer to understand routing without reading the node. Avoid generic text like "classified intent"; document enum values, route names, and legacy behavior.
- Keep graph state serialization-clean. Do not return or persist raw `AIMessage`, OpenAI response objects, parsed response wrappers, tool-call objects, or structured-output Pydantic model instances from nodes. Unpack them immediately to primitive fields.
- Do not add or copy non-LangChain/LangGraph decorators. Project decorators such as tracing, metrics, auth/context, retry, or logging decorators are intentionally out of scope and will be introduced manually later.

## Decorators Out Of Scope

Inventory decorators and instrumentation only to document that they are intentionally omitted:

```text
RuleEngine.process_intent -> @traced() in legacy path
LangGraphRuleEngine.process_intent -> do not add @traced() during this migration
Legacy gptcall helpers -> log_usage(...) deferred for ChatOpenAI-compatible follow-up
```

Rules:

- Do not copy legacy decorators to new LangGraph files.
- Do not add decorators to graph nodes, graph builders, handlers, or rule-engine methods unless explicitly requested.
- Non-LangChain/LangGraph decorators are out of scope, including `@traced()` and any future project decorators for metrics, retries, auth, logging, or context propagation.
- LangChain/LangGraph APIs such as graph builders, conditional edges, `Command`, and structured-output helpers remain in scope because they are framework constructs, not project decorators.
- Do not port legacy `log_usage(...)` calls in the LangGraph handler migration. ChatOpenAI-compatible usage logging is a deferred follow-up and should not block handler parity.
- The migration report should list omitted decorators as intentional out-of-scope work.

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

## Prompt And LLM Pattern

Migrate JSON-schema gateway helpers to Pydantic structured output, but preserve the legacy prompts. The old FSM prompts are curated behavioral assets; do not rewrite or shorten them unless there is a documented reason.

Prompt migration rules:

- Copy the legacy system prompt into `prompts.py` nearly verbatim.
- Preserve examples, decision tables, enum definitions, strict rules, negative instructions, tone constraints, and output-format expectations.
- Preserve contextual user-message construction: pass the same state/context variables the FSM prompt used, such as existing state, expected slot, consumed value, rate card, current email/mobile, or callback status.
- Remove only JSON-schema boilerplate that is now enforced by Pydantic; do not remove behavioral instructions.
- If the Pydantic model changes field names, adapt the prompt examples to the new names without losing examples.
- If any prompt content is removed, merged, or reworded, record it in the migration analysis report as a prompt parity risk.

Structured output fields must be descriptive at routing points:

```python
from typing import Literal
from pydantic import BaseModel, Field


class EmailConfirmation(BaseModel):
    confirmation: Literal["yes", "no", "ambiguous"] = Field(
        description=(
            "Legacy EMAIL_UPDATE confirmation classifier output: 'yes' routes to MFA_EMAIL, "
            "'no' aborts the journey with cancellation copy, and 'ambiguous' asks the user to confirm again."
        )
    )


async def classify_email_confirmation(state: EmailState) -> dict:
    llm = build_chat_openai(reasoning_effort="low")
    classifier = llm.with_structured_output(EmailConfirmation)
    decision = await classifier.ainvoke([
        ("system", EMAIL_CONFIRMATION_PROMPT),
        ("human", state.user_query),
    ])
    # Return plain serializable values only; do not put `decision` itself in graph state.
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

## Use Case Classification

| Dimension | Value | Notes |
| --- | --- | --- |
| Journey family | Slot-filling / widget-driven / backend-callback / hybrid / other | Pick the closest label; add a new label if needed. |
| Primary interrupt type | App widget / backend callback / user text / none / mixed | Identify what stops a turn and resumes later. |
| LLM usage | Classifier / extractor / confirmation / none / other | List all bounded LLM jobs. |
| Deterministic rules | Validation / selection / formatting / state normalization / none | Summarize non-LLM business logic. |
| External side effects | App action / backend execution request / final status display / none / other | State who owns the side effect. |

## Source To Target Map

| Component | FSM Source | LangGraph Target | Notes |
| --- | --- | --- | --- |

## FSM Inventory Checklist

| Item | Source Truth | Migrated? | Notes |
| --- | --- | --- | --- |
| Initial/default state fields |  |  |  |
| Persisted journey_state merge rules |  |  |  |
| Allowed additional_data callback fields |  |  |  |
| Per-turn reset flags |  |  |  |
| Ordered guard clauses / transition priority |  |  |  |
| LLM helpers and output schemas |  |  |  |
| Deterministic validators/selectors |  |  |  |
| Out-of-scope decorators, tracing, logging, and usage instrumentation |  |  |  |
| App-facing intent mapping |  |  |  |
| Abort/off-topic behavior |  |  |  |
| Success/failure/final-status behavior |  |  |  |
| Formatting-sensitive bot responses |  |  |  |
| Known legacy bugs or inconsistencies |  |  |  |

## Parity Matrix

| Area | FSM Behavior | LangGraph Behavior | Parity |
| --- | --- | --- | --- |

## Transition And Turn Coverage

| FSM Trigger / Guard | LangGraph Route / Node | Terminal This Turn? | Expected Next Callback/Input | Parity |
| --- | --- | --- | --- | --- |

## State Variable Flow

| State Field | FSM Role | LangGraph Role | Durable? | Reset Each Turn? | Source: persisted/app/user/LLM/rule | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Prompt And Classifier Parity

| LLM Helper | Legacy Prompt Sections Preserved? | Legacy Examples/Decision Tables Preserved? | Pydantic Model/Fields | Changed Or Removed Prompt Content | Risk |
| --- | --- | --- | --- | --- | --- |

For every row, compare the legacy helper prompt section-by-section. Mark risk as high when examples, decision tables, strict negative rules, enum definitions, or user-context variables were removed or summarized.

## Callback And Side-Effect Parity

| Action / Callback | FSM Emission | LangGraph Emission | Resume Field(s) | Owner | Parity |
| --- | --- | --- | --- | --- | --- |

## Out-Of-Scope Decorator And Observability Notes

| Decorator / Instrumentation | FSM Location | LangGraph Location | Action | Notes |
| --- | --- | --- | --- | --- |

## App Contract Parity

| App Intent/Response | FSM | LangGraph | Parity |
| --- | --- | --- | --- |

## Persistence And Transient State

| Field / Group | Saved By FSM | Saved By LangGraph | Excluded? | Notes |
| --- | --- | --- | --- | --- |

## Unseen Pattern Review

Use this section for future handlers that do not fit the current six journeys.

| Question | Answer |
| --- | --- |
| Does this handler introduce a new journey family or graph shape? |  |
| Does it need new shared models, validators, or adapters? |  |
| Does it introduce new callback fields or app-facing intents? |  |
| Does it own any backend side effect that must not run twice in shadow mode? |  |
| Does it require persistence fields not present in the FSM state? |  |
| Are there source behaviors intentionally fixed rather than preserved? |  |
| What remains unmapped or uncertain? |  |

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
