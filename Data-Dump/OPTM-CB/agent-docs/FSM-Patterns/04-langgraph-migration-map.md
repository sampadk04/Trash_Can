# LangGraph Migration Map

## Migration Goal

The current handler code already behaves like graphs, but the graph is hidden inside ordered `if` statements and flag checks. A LangGraph migration should make the state transitions explicit while keeping the app-facing contract stable:

```text
input:
  intent_type, user_query, journey_data, journey_state, additional_data

output:
  bot_response, intent_list, abort, additional_data
```

## Recommended State Shape

Use one typed state per journey, plus a small shared base.

```python
from typing import Any, Literal, Optional, TypedDict

class BaseJourneyState(TypedDict, total=False):
    user_query: str
    bot_response: str
    abort: Literal["yes", "no"]
    off_topic_count: int
    widget_response: Literal["yes", "no"]
    next_action: dict[str, Any]
```

For each journey, add domain fields:

```python
class FDState(BaseJourneyState, total=False):
    fd_amount: Optional[int]
    tenure: Optional[int]
    interest_rate: Optional[float]
    expected_slot: Optional[Literal["amount", "tenure"]]
    show_interest_rate_chart: Literal["true", "false"]
    raise_final_confirmation: Literal["yes", "no"]
```

During incremental migration, keep existing `"yes"/"no"` strings to avoid changing app behavior. Later, these can be normalized to booleans internally with an adapter at the boundary.

## Shared Node Types

### 1. Merge Input State

Purpose:

- start from persisted journey state,
- merge app callback `additional_data`,
- attach `user_query` and `journey_data`.

Current equivalent:

```text
handler._update_state_from_request(additional_data, journey_state)
```

### 2. Reset Turn Flags

Purpose:

- clear ephemeral UI/action flags at the beginning of each turn.

Current equivalents:

```text
FD: show_interest_rate_chart, raise_final_confirmation
UPI: show_contact_list, fetch_account_details, request_to_proceed
CC: fetch_card_details, fetch_payment_amount, fetch_account_details, raise_final_confirmation
Loan NOC: fetch_loan_list, show_address, raise_noc_request, show_redirection
Email/mobile: eligibility/get-new/MFA flags
```

### 3. Control Classifier

Purpose:

- classify abort/change/off-topic/none while inside a journey.

Current equivalents:

```text
FD intent_identification
UPI intent_identification
Credit card get_help
Email/mobile get_confirmation
Loan NOC check_confirmation
```

### 4. Slot Extractor

Purpose:

- use structured LLM output to extract domain values.

Current equivalents:

```text
FD update_amount, update_tenure
UPI extract_payee_details
```

### 5. Deterministic Validator

Purpose:

- enforce business rules without LLM involvement.

Current equivalents:

```text
FD validate_fd_amount, select_fd_plan
UPI validate_UPI_amount
RuleEngine.validate_journey_data
```

### 6. External Action Emitter

Purpose:

- set the app-facing next action and end this turn.

Current equivalents:

```text
get_intent_data()
```

In LangGraph, prefer a single field:

```python
{
    "next_action": {
        "intent_type": "Clarification",
        "intent": "PAY_TO_MOBILE.SHOW_CONTACT_LIST",
        "additional_data": {"payee_name": "Rahul"},
    }
}
```

Then adapt this back to the existing `intent_list`.

## Graph Pattern For Widget-Driven Journeys

Credit card is the cleanest example.

```text
START
  -> merge_inputs
  -> reset_flags
  -> route_resume_or_help
      -> request_card
      -> request_amount
      -> request_account
      -> prepare_confirmation
      -> classify_typed_help
      -> abort
  -> emit_action
  -> END
```

The graph should stop after emitting an app widget action. On the next API call, app results arrive through `additional_data`, and `merge_inputs` resumes the graph.

## Graph Pattern For Slot-Filling Journeys

FD and UPI are slot-filling flows.

```text
START
  -> merge_inputs
  -> reset_flags
  -> classify_control
  -> route_control
  -> extract_slot
  -> validate_slot
  -> route_missing_or_next
  -> external_selection_if_needed
  -> prepare_confirmation
  -> emit_action
  -> END
```

Each slot should be independently testable:

```text
FD amount:
  extract_amount -> validate_amount -> amount_done_or_ask_again

FD tenure:
  extract_tenure -> select_plan -> tenure_done_or_show_plans

UPI payee:
  extract_payee_amount -> maybe_clear_registered_payee -> show_contact_list
```

## Graph Pattern For Backend-Callback Journeys

Email/mobile/Loan NOC are app/backend callback flows. The handler mostly asks backend/app to do one action, then waits.

```text
START
  -> merge_inputs
  -> reset_flags
  -> route_by_known_backend_data
      -> request_eligibility
      -> request_user_input_validation
      -> request_mfa_or_create_request
      -> show_final_status
  -> emit_action
  -> END
```

These map well to LangGraph interrupts or per-turn terminal nodes.

## Persistence Options

The current system persists state in Redis through `StateManager`, not LangGraph checkpointers.

Recommended incremental approach:

1. Keep `RuleEngine` and `StateManager` as the persistence boundary.
2. Run the LangGraph graph for one request/turn using loaded state as input.
3. Return graph output as the same state dict currently saved by `RuleEngine`.
4. Only introduce LangGraph checkpointers later if you want native graph replay/debugging.

This avoids a risky persistence migration while still making handler flow explicit.

## Suggested Incremental Migration Order

1. Extract shared output adapter: convert flags or `next_action` to current `intent_list`.
2. Migrate the simplest graph first: `LOAN_NOC`.
3. Migrate widget-driven `PAY_CREDIT_CARD_BILL`.
4. Migrate paired backend-callback flows: `EMAIL_UPDATE`, then `MOBILE_UPDATE`.
5. Migrate `PAY_TO_MOBILE`.
6. Migrate `OPEN_FD` last because it has the richest LLM disambiguation and plan selection logic.

## What To Preserve Exactly

Preserve these externally visible behaviors unless product intentionally changes them:

- app-facing intent names such as `OPEN_FD.SHOW_PLANS`;
- `intent_type` values such as `Clarification`, `Execution`, `Redirection`;
- `abort` as a lower-case string;
- returned `additional_data` state shape;
- existing external callback fields such as `registered_payee_details`, `status`, `service_request_no`;
- one-action-per-turn behavior for widget/API handoffs.

## What To Improve During Migration

The main maintainability wins:

- explicit state schemas instead of untyped dicts;
- named nodes instead of hidden ordered guards;
- reusable nodes for reset flags, control classification, abort/off-topic handling, and output adaptation;
- deterministic validators isolated from LLM extractors;
- a single `next_action` object instead of many competing UI flags;
- tests per graph node and per transition.

## Minimal Adapter Sketch

```python
async def process_intent_with_graph(intent_type, user_query, journey_data, journey_state, additional_data):
    graph = graph_registry[intent_type]
    initial_state = {
        **journey_state,
        "user_query": user_query,
        "journey_data": journey_data,
        "additional_data": additional_data or {},
    }
    result = await graph.ainvoke(initial_state)
    intent_data = result.get("next_action") or legacy_get_intent_data(result)
    state_to_save = {k: v for k, v in result.items() if k not in {"bot_response", "next_action"}}
    return {
        "bot_response": result.get("bot_response", ""),
        "intent_list": [{
            "intent": intent_data.get("intent", ""),
            "label": intent_data.get("intent", ""),
            "intent_type": intent_data.get("intent_type", ""),
        }],
        "abort": state_to_save.get("abort", "no").lower(),
        "additional_data": state_to_save,
    }
```

This lets one handler at a time move to LangGraph while `RuleEngine` keeps the existing external interface.
