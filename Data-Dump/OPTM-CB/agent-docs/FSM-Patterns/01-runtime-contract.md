# Runtime Contract

## Core Mental Model

The current intent handler system is a set of hand-written finite-state machines. Each handler owns a Python dict called `state`. Every turn:

1. `RuleEngine` picks a handler class from `intent_type`.
2. It loads persisted per-journey state from Redis.
3. It merges app-provided `additional_data` into the handler state.
4. The handler runs ordered `if` blocks to advance one step.
5. The handler returns the full state plus `bot_response`.
6. `RuleEngine` removes `bot_response`, saves the rest back to Redis, and returns an app-facing intent.

Important source anchors:

- Handler registry and required journey data checks: `app/services/optimus_query_bot/rule_engine.py:14`
- Runtime invocation and state save: `app/services/optimus_query_bot/rule_engine.py:44`
- Redis per-journey state implementation: `app/services/optimus_query_bot/state_manager.py`

## Handler Registry

`RuleEngine.handler_classes` maps app intent names to handlers:

```text
OPEN_FD                -> FixedDepositHandler
PAY_CREDIT_CARD_BILL  -> CreditCardHandler
PAY_TO_MOBILE         -> UPIHandler
LOAN_NOC              -> LoanNocHandler
EMAIL_UPDATE          -> EmailChangeHandler
MOBILE_UPDATE         -> MobileChangeHandler
```

Only some journeys require base session data before handler execution:

```text
OPEN_FD               requires primary_balance, fixed_deposit_plans
PAY_CREDIT_CARD_BILL requires primary_balance
PAY_TO_MOBILE        requires primary_balance
```

## State Layers

There are two state layers relevant to handlers:

```text
journey_data
  Redis key: session:{ai_session_id}
  Durable app/session data: primary_balance, accounts, loans, cards,
  fixed_deposit_plans, journey_name, intent_id, customer profile.

journey_state
  Redis key: intent:{intent_id}:{journey_name}_state
  FSM-local state: fd_amount, tenure, card_details, abort, UI flags, etc.
```

`journey_data` is read-only from the handler perspective. `journey_state` is the mutable FSM snapshot.

## Per-Turn Sequence

```text
User/app turn
  |
  v
QueryBotService.intent_handler(...)
  |
  v
StateManager.get_journey_data(ai_session_id)
  |
  v
RuleEngine.process_intent(intent_type, user_query, journey_data, intent_id, additional_data)
  |
  +-- validate required journey_data
  +-- instantiate handler
  +-- load Redis journey_state
  +-- handler._update_state_from_request(additional_data, journey_state)
  +-- handler.handle(...)
  +-- handler.get_intent_data()
  +-- save returned state minus bot_response
  |
  v
Return bot_response, intent_list, abort, additional_data
```

## `additional_data` Is The App-to-FSM Resume Channel

Most flows ask the mobile app or backend to do something by setting a flag and returning an app-facing intent. On a later turn, the app sends results back through `additional_data`.

Examples:

```text
Handler sets show_contact_list = yes
  -> RuleEngine returns PAY_TO_MOBILE.SHOW_CONTACT_LIST
  -> app shows/selects a contact
  -> app later sends additional_data.registered_payee_details
  -> handler resumes from the next state
```

```text
Handler sets change_email_eligibility = yes
  -> app/backend checks eligibility
  -> app later sends additional_data.is_eligible and current_email
  -> handler asks for the new email
```

This is the most important migration concept: many "states" are not just chatbot turns; they are app interrupts/resume points.

## Output Contract

Handlers return a state dict like:

```text
{
  bot_response: "...",
  abort: "no",
  show_contact_list: "yes",
  payee_name: "Rahul",
  amount_to_be_paid: 500
}
```

`RuleEngine` persists everything except `bot_response`, then returns:

```text
{
  bot_response: "...",
  intent_list: [
    {
      intent: "PAY_TO_MOBILE.SHOW_CONTACT_LIST",
      label: "PAY_TO_MOBILE.SHOW_CONTACT_LIST",
      intent_type: "Clarification"
    }
  ],
  abort: "no",
  additional_data: persisted_state
}
```

`get_intent_data()` is effectively the adapter from internal flags to app-facing intent names.

## Current Architectural Constraint

The FSM implementation currently couples these concerns in each handler:

- state schema and defaults,
- merging persisted state,
- merging app callback data,
- LLM prompt calls,
- deterministic validation/business rules,
- routing/transition logic,
- UI/action flag generation,
- app-facing intent mapping.

The LangGraph migration should separate these concerns without changing the outer app contract unless absolutely necessary.
