# OPEN_FD Reference Pattern

This is a portable reference distilled from a completed `OPEN_FD` FSM-to-LangGraph migration. Do not treat any live migrated `OPEN_FD` files as required source material. Use this note as the durable example.

## Why This Pattern Matters

`OPEN_FD` is the richest current slot-filling journey. It combines:

- bounded control classification
- amount extraction and deterministic validation
- tenure extraction with bare-number disambiguation
- deterministic plan selection
- off-topic and abort handling
- final confirmation action emission
- preservation of previous valid state during invalid change attempts

If a future handler is simpler, keep the same structure but omit unneeded nodes.

## Portable File Structure

Use one usecase folder with this shape:

```text
<usecase_slug>/
  __init__.py
  models.py
  prompts.py
  nodes.py
  graph.py
  handler.py
```

Responsibilities:

| File | Responsibility |
| --- | --- |
| `models.py` | Journey state model and structured-output models. |
| `prompts.py` | Uppercase prompt constants for bounded classifiers/extractors. |
| `nodes.py` | Async node functions and private deterministic helpers. |
| `graph.py` | `Literal` route aliases, route functions, and `build_<usecase>_graph()`. |
| `handler.py` | Small adapter: invoke graph, resolve `NextAction`, persist durable state, return RuleEngine-compatible response. |

## State Model Pattern

Use one Pydantic state model extending `BaseJourneyState`. Preserve legacy durable field names and add only the transient fields required by graph nodes.

For an FD-like slot-filling flow, durable fields included:

```text
journey
fd_amount
tenure
tenure_description
interest_rate
show_interest_rate_chart
raise_final_confirmation
change_default
expected_slot
abort
off_topic_count
tenure_info
deposit/product metadata returned by selected plan
```

Transient fields included:

```text
journey_data
additional_data
consumed_value
control_intent
route_reason
next_action
```

Use `durable_state(..., extra_exclusions={...})` to remove transient and base-only fields that the legacy FSM did not persist.

## Structured Output Models

Keep bounded Pydantic output models near the state model:

```text
ControlDecision:
  intent enum: change_amount, change_tenure, change_default, abort, other, none, change_amount_and_tenure
  reasoning: concise explanation for debugging

AmountExtraction:
  bot_response
  amount field or null

TenureExtraction:
  bot_response
  tenure in days or null
  show_interest_rate_chart true/false
```

For other handlers, use the same pattern with journey-specific enums and fields.

## Graph Shape

The FD-like graph shape:

```text
START
  -> merge_inputs
  -> reset_flags
  -> classify_control
  -> route_control
      -> abort
      -> redirect_default_change
      -> handle_off_topic
      -> extract_amount
      -> extract_tenure
      -> prepare_confirmation
  -> END
```

After amount extraction:

```text
if expected_slot == "amount": END
elif tenure missing or tenure changed: extract_tenure
else: prepare_confirmation
```

After tenure extraction:

```text
if expected_slot == "tenure" and tenure missing: END
else: prepare_confirmation
```

Use explicit `Literal` aliases for route functions so node names stay visible and type-checkable.

## Node Patterns

`merge_inputs`:

- attach latest user query
- normalize legacy flags
- preserve persisted durable values
- merge only known app callback fields

`reset_flags`:

- clear one-turn UI/action flags
- clear `next_action`
- clear classifier/extractor scratch fields

`classify_control`:

- call shared `build_chat_openai(reasoning_effort="low")`
- use `.with_structured_output(...)`
- return only control decision fields

`extract_amount`:

- ask for amount when missing
- validate min, max, and available balance deterministically
- on invalid replacement, preserve any previous valid amount and stop the turn
- set `expected_slot = "amount"` when asking again

`extract_tenure`:

- convert explicit duration units to days
- use `expected_slot` to interpret bare numbers
- use `consumed_value` so one bare number is not reused as both amount and tenure
- show plan chart when tenure is missing, ambiguous, or unavailable

`prepare_confirmation`:

- require all durable business fields needed for final confirmation
- emit the final confirmation app intent through `NextAction`

## Prompt Parity Rules

When shortening legacy prompts, preserve:

- all enum labels and their meanings
- explicit examples for abort and off-topic behavior
- amount signals such as currency symbols, rupees, lakhs, thousands, `k`, and crore
- tenure signals such as days, months, years, `for X`, `X duration`, and `X period`
- expected-slot rules for bare numbers
- consumed-value rules that block reusing the same numeric token
- rules for default changes such as nominee, auto-renewal, payout, or maturity instructions

The graph prompt does not need to be byte-for-byte identical, but the report must call out any prompt compression risk.

## Deterministic Validation Rules

Keep these as plain helper functions, not LLM decisions:

- amount lower bound
- amount upper bound
- balance check
- duration-to-days conversion
- matching plan filter
- selected-plan sorting by highest interest rate, then narrowest matching tenure range
- final confirmation missing-field checks

## Action And Persistence Pattern

Action nodes should set `next_action` directly:

```text
default journey clarification
show available plans
raise final confirmation
redirection
empty intent for abort
```

The handler adapter should still include legacy fallback mapping from flags to `NextAction` as a safety net. Persist durable state only after excluding graph-only fields.

## Parity Risks To Check

Use the report to explicitly verify:

- invalid change attempts do not erase prior valid state unless the FSM does so
- off-topic count increments and abort threshold match legacy behavior
- app-facing intent names and intent types match
- prompt compression preserves all important disambiguation examples
- fields added by `BaseJourneyState` do not leak into saved legacy state
- every one-turn flag is reset before the current turn's action is emitted
