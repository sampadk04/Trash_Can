---
name: fsm-to-langgraph
description: Translate Optimus Query Bot FSM-based intent handlers into parallel LangGraph-based handlers. Use when migrating, reviewing, scaffolding, or testing code under app/services/optimus_query_bot/intent_handlers, app/services/optimus_query_bot/langgraph_intent_handlers, or app/services/optimus_query_bot/langgraph_rule_engine.py, while preserving the existing RuleEngine contract, app-facing intents, Redis state shape, and V1 soft-migration strategy.
---

# FSM To LangGraph

## Core Rule

Re-architect one FSM intent handler at a time into a parallel LangGraph implementation. Preserve the existing behavior and app contract first; make the flow more interpretable second. Do not delete or replace FSM handlers in V1.

Keep work scoped to:

- `app/services/optimus_query_bot/langgraph_intent_handlers/`
- `app/services/optimus_query_bot/langgraph_rule_engine.py`
- minimal selector/config wiring only when required
- read-only reference from `app/services/optimus_query_bot/intent_handlers/*.py`
- read-only contract reference from `app/services/optimus_query_bot/rule_engine.py`

Avoid non-trivial edits outside the Optimus Query Bot handler/engine boundary unless the user explicitly asks for broader integration.

## Reference Loading

Load only the references needed for the current handler:

- Read `references/codebase-contract.md` before any migration or review to preserve runtime behavior.
- Read `references/migration-playbook.md` before implementing or planning a LangGraph handler.
- Read `references/handler-patterns.md` for the specific intent being migrated.
- Read `references/langgraph-langchain-minimal.md` when writing graph, state, routing, or structured-output code.

If the local repo has `agent-docs/`, prefer those files as the source of truth when they differ from this skill. Start with `agent-docs/Migration-Guide/README.md`, then the relevant `agent-docs/FSM-Patterns/*.md` and handler source.

## Migration Workflow

1. Identify the target intent and source FSM handler.
2. Read `rule_engine.py` and the source handler's `initialize_state`, `_update_state_from_request`, `handle`, helper classifiers/extractors, validators, and `get_intent_data`.
3. Build a parity map: persisted fields, one-turn flags, app callback fields, app-facing intents, abort behavior, status handling, and edge cases.
4. Create or extend the parallel LangGraph package; do not edit the FSM handler except for tiny integration hooks that are strictly necessary.
5. Model state with Pydantic `BaseModel` classes and `Field` descriptions. Use `ConfigDict(extra="allow")` during V1 so unknown legacy keys are not dropped.
6. Split the FSM into explicit nodes:
   - merge persisted state and allowed callback fields
   - reset one-turn UI/action flags
   - classify bounded user intent, if needed
   - extract slots, if needed
   - validate deterministic business rules
   - emit a `next_action`
7. Use `StateGraph`, named nodes, and conditional edges. Use `Command` only when one node must both update state and choose the next node.
8. Add a small handler adapter exposing `process(user_query, journey_data, journey_state, additional_data)` for `LangGraphRuleEngine`.
9. Add the handler to the LangGraph registry only after parity tests exist.
10. Verify node-level routing, callback resume behavior, adapter output, persisted state, and fallback to FSM.

## Design Constraints

- Keep `bot_response`, `intent_list`, `abort`, and `additional_data` response shape compatible with `RuleEngine`.
- Keep external `abort` as lower-case `"yes"` or `"no"`.
- Keep app-facing intent names such as `OPEN_FD.SHOW_PLANS` and `PAY_TO_MOBILE.SHOW_CONTACT_LIST`.
- Keep one-action-per-turn behavior for widgets, MFA, backend execution, and final status callbacks.
- Keep Redis persistence owned by `StateManager`; do not add LangGraph checkpointers as the primary V1 persistence layer.
- Store only durable business state. Exclude `bot_response`, `next_action`, `user_query`, `journey_data`, `additional_data`, and classifier scratch fields before saving unless intentionally durable.
- Use `ChatOpenAI` with Pydantic structured output for migrated LLM classifier/extractor nodes. Do not recreate legacy JSON-schema gateway calls inside graph nodes unless the user explicitly requires it for compatibility.
- Prefer deterministic validators over LLM reasoning for business rules.
- Keep classifiers narrow and bounded; these handlers are workflow graphs, not open-ended agents.

## Output Shape Pattern

Prefer a normalized `next_action` field inside graph state:

```python
NextAction(
    intent="PAY_TO_MOBILE.SHOW_CONTACT_LIST",
    intent_type="Clarification",
    additional_data={"payee_name": state.payee_name},
)
```

Convert it in the LangGraph rule-engine adapter to the existing response:

```python
{
    "bot_response": state.bot_response,
    "intent_list": [{
        "intent": action.intent,
        "label": action.intent,
        "intent_type": action.intent_type,
    }],
    "abort": state_to_save.get("abort", "no").lower(),
    "additional_data": state_to_save | action.additional_data,
}
```

Use legacy `get_intent_data()` only as a parity reference. Do not import the FSM handler at runtime just to derive graph output.

## Testing Expectations

For every migrated handler, cover:

- state defaults and legacy field compatibility
- merge of persisted state plus allowed `additional_data`
- reset of one-turn flags
- all app-facing intents reachable
- abort and off-topic behavior
- widget/backend callback resume paths
- status success and failure paths
- adapter output shape and saved-state exclusions
- feature flag or registry fallback to FSM for disabled intents

When comparing FSM and LangGraph, use the same `journey_state`, `journey_data`, `user_query`, and `additional_data`, then compare app-facing intent, abort, bot-response category, and durable state keys.
