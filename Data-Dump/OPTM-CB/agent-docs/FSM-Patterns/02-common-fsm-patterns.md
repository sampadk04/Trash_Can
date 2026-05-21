# Common FSM Patterns

## Pattern 1: Ordered Guard Clauses As States

The handlers do not define explicit state enums. Instead, the active state is inferred from missing data and flags.

Example shape:

```python
if not state["fd_amount"]:
    collect_amount()
    return state

if not state["tenure"]:
    collect_tenure()
    return state

raise_final_confirmation()
return state
```

The first matching guard wins. This makes flow compact, but it hides the state machine because state names are implicit.

LangGraph translation:

```text
START -> classify_or_resume -> route_next
route_next -> collect_amount | collect_tenure | final_confirmation | END
```

## Pattern 2: Reset Ephemeral UI Flags Every Turn

Handlers reset UI/action flags at the start of each turn:

```text
show_contact_list = no
fetch_account_details = no
request_to_proceed = no
```

Then exactly one step sets the flag needed for the current response.

Meaning:

- persisted facts should survive (`fd_amount`, `payee_name`, `account_details`);
- one-turn commands should be re-issued only when needed (`SHOW_CONTACT_LIST`, `MFA_EMAIL`);
- stale UI flags should not trigger old widgets again.

LangGraph translation:

- Add a `reset_turn_flags` node at the start of each graph.
- Or make every action node return a complete `next_action` object instead of many `"yes"/"no"` flags.

## Pattern 3: Slot Filling With Validation

Several journeys collect missing slots, validate them, then continue.

Common sequence:

```text
extract candidate value
  |
  v
validate business rule
  |
  +-- invalid/missing -> ask again and set expected slot/UI flag
  |
  v
save value and continue
```

Examples:

- FD amount extraction plus min/max/balance validation.
- FD tenure extraction plus available-plan selection.
- UPI payee and amount extraction plus balance validation.
- Email/mobile collection through app-side validators.

LangGraph translation:

```text
extract_amount -> validate_amount -> route_amount_result
```

Keep extraction and validation as separate nodes because extraction is LLM-shaped while validation is deterministic.

## Pattern 4: Bounded LLM Classifiers

The code uses LLMs in constrained ways, usually with JSON schemas:

```text
FD:
  intent_identification -> change_amount, change_tenure, abort, other, none
  update_amount        -> fd_amount
  update_tenure        -> tenure, show_interest_rate_chart

UPI:
  intent_identification -> change_payee_or_amount, abort, other, none
  extract_payee_details -> payee_name, amount_to_be_paid

Email/mobile:
  get_confirmation -> yes, no, ambiguous

Loan NOC:
  check_confirmation -> yes, no

Credit card:
  get_help -> widget_issue, abort, other
```

These are not open-ended agents. They are typed classifier/extractor nodes.

LangGraph translation:

- Use one node per classifier/extractor.
- Use structured output for schema enforcement.
- Route with conditional edges or `Command`.

## Pattern 5: App Widget Interrupt And Resume

Many steps are really "ask the app to show a widget, then wait for app callback."

Examples:

```text
Credit card:
  SHOW_CREDIT_CARDS -> app returns card_details
  SHOW_AMOUNT       -> app returns payment_amount
  SHOW_ACCOUNTS     -> app returns account_details

UPI:
  SHOW_CONTACT_LIST -> app returns registered_payee_details
  SHOW_ACCOUNTS     -> app returns account_details

Loan NOC:
  SELECT_NOC_LOAN   -> app returns noc_loan
  CONFIRM_ADDRESS   -> app returns/sets noc_address

Email/mobile:
  CHANGE_*_ELIGIBILITY -> app returns is_eligible and current value
  VALIDATE_*           -> app returns new value
  MFA_*                -> app returns status/service_request_no
```

LangGraph translation:

- Represent these as interrupt points or terminal per-turn nodes.
- The graph may return `next_action` and stop for this HTTP turn.
- On the next invocation, merge app callback data and resume routing.

## Pattern 6: Final Confirmation Before Execution

Most transactional flows assemble a summary and ask the user/app to confirm before execution.

Examples:

- FD: `OPEN_FD.RAISE_FINAL_CONFIRMATION`
- UPI: `PAY_TO_MOBILE.RAISE_FINAL_CONFIRMATION`
- Credit card: `PAY_CREDIT_CARD_BILL.RAISE_FINAL_CONFIRMATION`
- Loan NOC: `LOAN_NOC.CREATE_NOC_REQUEST`
- Email/mobile: MFA before final status

The current handler often stops at "raise confirmation"; the actual execution is app/backend-owned and returns status later.

LangGraph translation:

```text
prepare_confirmation -> emit_confirmation_action -> END_FOR_TURN
```

Do not model backend execution inside the graph unless the current handler already owns it.

## Pattern 7: Abort And Off-Topic Counters

Several handlers use local LLM classifiers to detect abort/off-topic inputs during an active journey.

Common behavior:

```text
intent == abort -> abort = yes
intent == other -> off_topic_count += 1
off_topic_count > threshold -> abort = yes
otherwise remind user journey is active
```

This is repeated in FD, UPI, and credit card. Loan NOC and email/mobile have narrower confirmation handling.

LangGraph translation:

- Use a shared `classify_journey_control` node pattern where appropriate.
- Use a deterministic `route_control_intent` function after classifier output.

## Pattern 8: `get_intent_data()` As Output Adapter

Each handler has a priority-ordered mapping from flags to app-facing intent.

Example:

```text
if raise_final_confirmation == yes -> OPEN_FD.RAISE_FINAL_CONFIRMATION
if show_interest_rate_chart == true -> OPEN_FD.SHOW_PLANS
if abort == yes -> empty intent
else -> OPEN_FD
```

This adapter is crucial because the app does not consume raw internal state. It consumes intent names and `intent_type`.

LangGraph translation:

- Keep an adapter layer during migration.
- Prefer returning a single structured `next_action` from graph state, then convert it to the current `intent_list` shape.
