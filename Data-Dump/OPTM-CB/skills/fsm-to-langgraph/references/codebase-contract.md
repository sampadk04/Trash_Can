# Codebase Contract

## Runtime Boundary

The Optimus Query Bot execution journeys are currently hand-written FSMs under:

```text
app/services/optimus_query_bot/intent_handlers/
```

`RuleEngine.process_intent(...)` is the contract to preserve:

```text
input:
  intent_type
  user_query
  journey_data
  intent_id
  additional_data
  persisted journey_state from Redis

output:
  bot_response
  intent_list
  abort
  additional_data
```

Current per-turn sequence:

```text
RuleEngine
  -> validate required journey_data
  -> instantiate handler
  -> load journey_state via StateManager
  -> handler._update_state_from_request(additional_data, journey_state)
  -> handler.handle(user_query, journey_data, journey_state)
  -> handler.get_intent_data()
  -> save state minus bot_response
  -> return bot_response, intent_list, abort, additional_data
```

Do not change the caller-facing response shape for V1.

## Handler Registry

Current intents:

```text
OPEN_FD                -> FixedDepositHandler
PAY_CREDIT_CARD_BILL  -> CreditCardHandler
PAY_TO_MOBILE         -> UPIHandler
LOAN_NOC              -> LoanNocHandler
EMAIL_UPDATE          -> EmailChangeHandler
MOBILE_UPDATE         -> MobileChangeHandler
```

Required `journey_data` checks:

```text
OPEN_FD               requires primary_balance, fixed_deposit_plans
PAY_CREDIT_CARD_BILL requires primary_balance
PAY_TO_MOBILE        requires primary_balance
```

Keep this validation in the rule engine boundary. It is not a graph transition.

## State Layers

`journey_data` is session/app data and should be read-only from handler nodes. It includes values such as `primary_balance`, accounts, loans, cards, `fixed_deposit_plans`, `journey_name`, `intent_id`, and customer profile data.

`journey_state` is per-intent durable handler state saved under `intent:{intent_id}:{journey_name}_state`. It contains FSM-local values such as `fd_amount`, `tenure`, `card_details`, `registered_payee_details`, `abort`, status, and one-turn UI flags.

`additional_data` is the app/backend resume channel. A graph node emits an app-facing action and stops for the HTTP turn; the next request supplies callback fields through `additional_data`.

Common callback fields:

```text
registered_payee_details
account_details
card_details
payment_amount
noc_loan
noc_address
is_eligible
current_email
current_mobile
new_email
new_mobile
status
service_request_no
widget_response
```

Merge only fields that the handler explicitly accepts.

## Compatibility Rules

Preserve:

- app-facing intent names
- `intent_type` values such as `Clarification`, `Execution`, and `Redirection`
- lower-case string `abort`
- returned `additional_data` as durable state plus action payload
- one-action-per-turn behavior
- callback field names understood by the mobile app/backend
- Redis persistence through `StateManager`

Exclude from persisted graph state unless intentionally durable:

```text
bot_response
next_action
user_query
journey_data
additional_data
control_intent
route
route_reason
extraction scratch fields
```

## Existing Coupling To Separate

FSM handlers currently mix state defaults, callback merge, LLM prompt calls, validation, routing, one-turn flags, and app-facing output mapping in one class. LangGraph migration should separate these into models, nodes, graph edges, validators, prompts, and adapters while keeping the same behavior.
