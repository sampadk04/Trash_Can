# Optimus Query Bot Soft FSM to LangGraph Migration Guide

## 1. Goal And Non-Goals

This guide describes a soft V1 migration of the Optimus Query Bot intent handlers from implicit finite-state machines to explicit LangGraph graphs.

The migration goal is interpretability and maintainability, not a product redesign. Because the current FSM handlers are production code, the LangGraph implementation must be introduced in parallel and remain backwards compatible. At any point during rollout, the platform should be able to use either the existing FSM handler or the new LangGraph handler for a supported intent.

Core migration posture:

- keep existing FSM files untouched except for small integration hooks that are strictly necessary
- add a new `langgraph_rule_engine.py` alongside the existing `rule_engine.py`
- add a new `langgraph_intent_handlers/` package alongside the existing `intent_handlers/`
- migrate one intent at a time by adding a parallel LangGraph use-case handler
- preserve the current request/response contract so callers do not need to know which engine served the turn

In scope:

- new graph code under `app/services/optimus_query_bot/langgraph_intent_handlers/`
- new graph rule engine at `app/services/optimus_query_bot/langgraph_rule_engine.py`
- minimal engine-selection wiring outside these files, only if needed to choose FSM or LangGraph at runtime
- read-only behavioral reference from `app/services/optimus_query_bot/intent_handlers/*.py`
- read-only contract reference from `app/services/optimus_query_bot/rule_engine.py`

Out of scope for V1:

- changing mobile app intent names
- replacing or deleting existing FSM handlers
- moving Redis state ownership away from `StateManager`
- adding LangGraph checkpointers as the primary persistence layer
- changing backend execution responsibilities for payments, MFA, eligibility, NOC creation, or final confirmations
- broad chatbot routing changes outside intent handlers

## 2. Current Contract To Preserve

`RuleEngine.process_intent(...)` currently provides this per-turn boundary:

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

For V1, keep this boundary. The selected engine should run for one request turn, return the updated journey state, and save that state back to Redis through `StateManager`.

Important compatibility rules:

- Keep app-facing intents, for example `OPEN_FD.SHOW_PLANS` and `PAY_TO_MOBILE.SHOW_CONTACT_LIST`.
- Keep `intent_type` values such as `Clarification`, `Execution`, and `Redirection`.
- Keep `abort` as `"yes"` or `"no"` strings at the external boundary.
- Keep `additional_data` as the saved journey state.
- Preserve one-action-per-turn behavior for widget and backend handoffs.
- Preserve callback field names such as `registered_payee_details`, `account_details`, `status`, `service_request_no`, `is_eligible`, `current_email`, and `current_mobile`.

## 3. Soft Migration Principles

The LangGraph migration should behave like an alternate engine, not an in-place rewrite.

### 3.1 Parallel Engines

Keep the current production path:

```text
rule_engine.py
  -> intent_handlers/
       fixed_deposit.py
       upi.py
       credit_card.py
       loan_noc.py
       email_update.py
       mobile_no_update.py
```

Add the graph path beside it:

```text
langgraph_rule_engine.py
  -> langgraph_intent_handlers/
       ...
```

The two engines should expose the same high-level `process_intent(...)` method shape so a caller can select either engine without changing the app response contract.

### 3.2 Runtime Selection

Use an explicit runtime selector to choose the engine. The selector can be controlled by config, feature flag, allowlist, or a request-level experiment flag.

Recommended selection behavior:

- default to FSM for all intents
- enable LangGraph per intent, not globally
- support quick rollback by switching an intent back to FSM
- avoid switching engines in the middle of an active journey unless state parity has been proven for that intent

If mid-journey switching is required, the LangGraph state model must remain compatible with the FSM journey state for that intent. Otherwise, store and honor an engine choice at journey start.

Recommended journey-start marker:

```text
journey_state.engine = "fsm" | "langgraph"
```

Only add this marker if the current state adapter excludes it before calling old FSM handlers, or if each migrated FSM handler safely ignores unknown persisted keys.

### 3.3 State Compatibility

For V1, LangGraph states should persist the same durable keys as the FSM handlers. This keeps Redis state readable by both implementations.

Graph-only fields should be excluded before persistence unless they are intentionally shared. Examples of graph-only fields:

- `next_action`
- classifier scratch fields such as `control_intent`
- runtime input fields such as `journey_data` and `additional_data`
- tracing metadata

### 3.4 Rollout Modes

Use these rollout modes as confidence grows:

```text
FSM only
  Production default.

LangGraph dev only
  Graph handlers run in tests or lower environments.

Shadow mode
  FSM response is returned, LangGraph may run in the background for diffing where safe.

Canary mode
  Selected intents or sessions use LangGraph as the returned response.

Full intent migration
  One intent defaults to LangGraph, with FSM fallback still available.
```

Shadow mode must not execute external side effects twice and must not persist graph output back to Redis. Run it with a cloned state snapshot and log only sanitized diffs. It is safest for pure handler turns, not turns that emit backend execution actions.

## 4. Target Architecture

Each LangGraph intent handler becomes a small graph with this shape:

```text
START
  -> merge_inputs
  -> reset_turn_flags
  -> classify_or_route
  -> domain nodes
  -> set_next_action
  -> END
```

The graph should make three things visible:

- State schema: what the journey knows.
- Nodes: what work happens at each step.
- Edges: why the flow moves to the next step.

Recommended folder layout:

```text
app/services/optimus_query_bot/
  rule_engine.py                         # existing FSM engine, remains production-safe
  intent_handlers/                       # existing FSM handlers, remains intact

  langgraph_rule_engine.py               # new parallel LangGraph engine
  langgraph_intent_handlers/
    __init__.py
    models/
      __init__.py
      base.py                            # BaseJourneyState, NextAction, common literals
      actions.py                         # app-facing action models and constants
    utils/
      __init__.py
      adapters.py                        # graph-state to rule-engine-compatible response adapter
      llm.py                             # ChatOpenAI factory
      state.py                           # merge, normalize, persistence helpers
      validators.py                      # shared deterministic validators
    usecase_handlers/
      __init__.py
      loan_noc/
        __init__.py
        graph.py
        models.py
        nodes.py
        prompts.py
        handler.py
      credit_card/
        ...
      email_update/
        ...
      mobile_update/
        ...
      upi/
        ...
      <usecase_slug>/
        ...
```

Each `usecase_handlers/<intent>/handler.py` should expose one small adapter class or function consumed by `langgraph_rule_engine.py`. The actual graph construction should live in `graph.py`, while state models and node implementations stay close to that use case.

### 4.1 Coding Conventions

Use the `OPEN_FD` migration lessons as a style reference, but do not depend on live migrated `OPEN_FD` files being present:

- migrate one intent/use case at a time
- use lower snake_case use-case folders such as `open_fd`, `loan_noc`, and `pay_to_mobile`
- keep state and structured-output models in `models.py`
- keep prompts as uppercase constants in `prompts.py`
- keep async node functions and private deterministic helpers in `nodes.py`
- keep `Literal` route aliases, route functions, and `build_<usecase>_graph()` in `graph.py`
- keep the graph adapter small in `handler.py`: build/invoke graph, resolve `NextAction`, call `durable_state`, and return the existing RuleEngine response shape
- make nodes return partial dictionaries; do not mutate the input state in place
- set `next_action` in action nodes and keep legacy flag-to-action fallback only as adapter safety
- use shared `BaseJourneyState`, `NextAction`, `build_chat_openai`, and `durable_state`
- use `extra_exclusions` for base fields that are not durable for a specific legacy FSM
- preserve legacy prompt labels, examples, and disambiguation rules when migrating to structured output

## 5. Shared Pydantic Models

Use Pydantic models rather than `TypedDict`. Field descriptions are important because the same models can guide structured output extraction and make state self-documenting.

Use permissive extra handling during V1 so unknown legacy fields are not accidentally dropped while handlers are migrated incrementally.

```python
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


YesNo = Literal["yes", "no"]


class NextAction(BaseModel):
    intent: str = Field(description="App-facing intent name to return for this turn.")
    intent_type: str = Field(description="App-facing intent type such as Clarification, Execution, or Redirection.")
    additional_data: dict[str, Any] = Field(default_factory=dict, description="Optional action-specific payload for the app.")


class BaseJourneyState(BaseModel):
    model_config = ConfigDict(extra="allow")

    journey: str = Field(description="Internal journey name used for debugging and persistence.")
    user_query: str = Field(default="", description="Latest user utterance for this graph turn.")
    bot_response: str = Field(default="", description="Customer-facing response for this turn.")
    abort: YesNo = Field(default="no", description="Whether this journey should terminate after this turn.")
    off_topic_count: int = Field(default=0, description="Number of off-topic turns seen inside the current journey.")
    widget_response: YesNo = Field(default="no", description="Whether this turn resumed from an app widget callback.")
    next_action: NextAction | None = Field(default=None, description="Normalized app action selected by the graph.")
```

Example handler state:

```python
class LoanNocState(BaseJourneyState):
    journey: str = Field(default="LOAN_NOC", description="Loan NOC journey identifier.")
    noc_loan: str | None = Field(default=None, description="Loan selected by the user for NOC generation.")
    noc_address: str | None = Field(default=None, description="Address shown to the user for NOC delivery confirmation.")
    status: Literal["success", "failure"] | None = Field(default=None, description="Backend NOC request status.")
    service_request_no: str | None = Field(default=None, description="Backend service request number for the NOC request.")
    fetch_loan_list: YesNo = Field(default="no", description="One-turn flag requesting the loan selector widget.")
    show_address: YesNo = Field(default="no", description="One-turn flag requesting address confirmation UI.")
    raise_noc_request: YesNo = Field(default="no", description="One-turn flag requesting backend NOC creation.")
    show_redirection: YesNo = Field(default="no", description="One-turn flag requesting address-update redirection.")
```

## 6. LLM Client Pattern

Do not use the existing LLM gateway for migrated graph nodes. Use `ChatOpenAI` with structured output.

Use the shared factory in `app/services/optimus_query_bot/langgraph_intent_handlers/utils/llm.py`. Current shape:

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

If the installed `langchain-openai` version changes client keyword names, keep the same SSL behavior and adapt only this factory. All graph nodes should import the factory rather than constructing model clients directly.

Use low reasoning effort for bounded classifiers and extractors. Increase only if a specific handler needs more careful disambiguation.

## 7. Structured Output Models

Replace JSON-schema dictionaries with Pydantic classes.

```python
from typing import Literal
from pydantic import BaseModel, Field


class LoanNocConfirmation(BaseModel):
    confirmation: Literal["yes", "no"] = Field(
        description="Whether the user explicitly confirms the displayed NOC delivery address."
    )


class EmailConfirmation(BaseModel):
    confirmation: Literal["yes", "no", "ambiguous"] = Field(
        description="Whether the user confirms, rejects, or gives an unclear response to the email update confirmation."
    )


class UpiExtraction(BaseModel):
    bot_response: str = Field(description="Customer-facing response only when clarification or acknowledgement is needed.")
    payee_name: str | None = Field(description="UPI payee name from the user, transliterated to English if needed.")
    amount_to_be_paid: float | None = Field(description="Payment amount from the user, or null if missing.")
```

Node pattern:

```python
async def classify_address_confirmation(state: LoanNocState) -> dict:
    llm = build_chat_openai(reasoning_effort="low")
    classifier = llm.with_structured_output(LoanNocConfirmation)
    decision = await classifier.ainvoke([
        ("system", "Classify whether the user explicitly confirms the displayed NOC address."),
        ("human", state.user_query),
    ])
    return {"address_confirmation": decision.confirmation}
```

## 8. Graph State And Runtime Context

Do not persist large or request-only dependencies in state. Put request dependencies in LangGraph runtime context or pass them through the input state and exclude them before saving.

For V1, a practical state input can include:

```python
class JourneyRuntimeInput(BaseModel):
    user_query: str = Field(description="Latest user utterance.")
    journey_data: dict[str, Any] = Field(description="Read-only session and app data loaded by the selected rule engine.")
    additional_data: dict[str, Any] = Field(default_factory=dict, description="App callback data for the current turn.")
```

Before saving state, exclude:

- `bot_response`
- `next_action`
- `journey_data`
- `additional_data`
- transient classifier results that should not survive the turn

## 9. Shared Nodes

### 9.1 Merge Inputs

Current equivalent: each handler's `_update_state_from_request(...)`.

Responsibilities:

- start with persisted state
- merge known callback fields from `additional_data`
- attach `user_query`
- normalize external strings such as `"YES"` to `"yes"`

Do not blindly merge all app data into graph state. Each handler should define allowed callback fields.

### 9.2 Reset Turn Flags

Current handlers reset UI flags at the beginning of each turn. Keep that behavior.

Example:

```python
def reset_loan_noc_flags(state: LoanNocState) -> dict:
    return {
        "bot_response": "",
        "fetch_loan_list": "no",
        "show_address": "no",
        "raise_noc_request": "no",
        "show_redirection": "no",
        "next_action": None,
    }
```

### 9.3 Control Classifier

Use one bounded classifier per journey family:

- FD: `change_amount`, `change_tenure`, `change_amount_and_tenure`, `change_default`, `abort`, `other`, `none`
- UPI: `change_payee_or_amount`, `abort`, `other`, `none`
- Credit card: `widget_issue`, `abort`, `other`
- Email/mobile: `yes`, `no`, `ambiguous`
- Loan NOC: strict `yes`, `no`

Keep classifiers narrow. They should not perform validation or execute business rules.

### 9.4 Deterministic Validators

Keep validators as plain functions:

- FD amount min, max, and balance validation
- FD plan selection
- UPI amount balance validation
- callback completeness checks

### 9.5 Next Action Adapter

Prefer a single `next_action` field inside graph state. Convert it back to the existing `intent_list` contract in `LangGraphRuleEngine`.

```python
def response_from_graph_state(state: BaseJourneyState) -> dict:
    action = state.next_action or NextAction(intent=state.journey, intent_type="Clarification")
    state_to_save = state.model_dump(
        exclude={"bot_response", "next_action", "user_query", "journey_data", "additional_data"},
        exclude_none=False,
    )
    return {
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

During migration, use each FSM handler's legacy `get_intent_data()` as a parity reference. The LangGraph handlers should set `next_action` directly rather than importing the FSM handler at runtime.

## 10. Parallel Rule Engine Strategy

Do not replace `RuleEngine` in V1. Add a new `LangGraphRuleEngine` in `app/services/optimus_query_bot/langgraph_rule_engine.py`.

Both engines should keep the same external method shape:

```python
class LangGraphRuleEngine:
    def __init__(self):
        self.state_manager = StateManager()
        self.graph_handlers = {
            "LOAN_NOC": LoanNocGraphHandler(),
            # Add one use case at a time.
        }

        self.INTENT_REQUIRED_KEYS = {
            "OPEN_FD": ["primary_balance", "fixed_deposit_plans"],
            "PAY_CREDIT_CARD_BILL": ["primary_balance"],
            "PAY_TO_MOBILE": ["primary_balance"],
        }
```

The graph engine should perform the same outer responsibilities as the FSM engine:

- validate required `journey_data`
- load journey state from `StateManager`
- invoke the graph-backed handler
- save returned state to `StateManager`
- return `bot_response`, `intent_list`, `abort`, and `additional_data`

Suggested graph dispatch:

```python
handler = self.graph_handlers.get(intent_type)
if not handler:
    return {
        "status": "error",
        "message": f"LangGraph handler not enabled for intent type: {intent_type}",
        "bot_response": "I'm sorry, I don't understand that request.",
    }

response = await handler.process(
    user_query=user_query,
    journey_data=journey_data,
    journey_state=journey_state,
    additional_data=additional_data or {},
)
```

The legacy `RuleEngine` can remain unchanged. A higher-level selector can choose which engine to instantiate.

Example selector:

```python
class OptimusIntentEngineSelector:
    def __init__(self, fsm_engine: RuleEngine, graph_engine: LangGraphRuleEngine, config):
        self.fsm_engine = fsm_engine
        self.graph_engine = graph_engine
        self.config = config

    def use_langgraph(self, intent_type: str) -> bool:
        enabled_intents = self.config.get("LANGGRAPH_ENABLED_INTENTS", [])
        return intent_type in enabled_intents and intent_type in self.graph_engine.graph_handlers

    async def process_intent(self, intent_type: str, **kwargs):
        if self.use_langgraph(intent_type):
            return await self.graph_engine.process_intent(intent_type=intent_type, **kwargs)
        return await self.fsm_engine.process_intent(intent_type=intent_type, **kwargs)
```

If the current call site cannot easily introduce a selector, keep `RuleEngine` as the default and add a minimal opt-in branch there that delegates to `LangGraphRuleEngine` only when a feature flag is enabled. That branch should be tiny and reversible.

### 10.1 Handler Registry

Use an incremental graph registry so one handler can move at a time.

```python
GRAPH_HANDLER_REGISTRY = {
    "LOAN_NOC": LoanNocGraphHandler,
    # "PAY_CREDIT_CARD_BILL": CreditCardGraphHandler,
    # "EMAIL_UPDATE": EmailUpdateGraphHandler,
    # Add only after each handler passes parity tests.
}
```

Keep `validate_journey_data(...)` behavior identical to the FSM engine for V1. It is an outer contract check, not a handler-specific graph transition.

## 11. Handler Graph Maps

### 11.1 LOAN_NOC

Migrate first. It is mostly deterministic with one strict confirmation classifier.

Graph:

```text
START
  -> merge_loan_noc_inputs
  -> reset_loan_noc_flags
  -> route_loan_noc
      -> request_loan_selection
      -> request_address_confirmation
      -> classify_address_confirmation
      -> request_noc_creation
      -> show_redirection
      -> show_final_status
  -> END
```

Routing rules:

- missing `noc_loan` -> `LOAN_NOC.SELECT_NOC_LOAN`
- missing `noc_address` -> `LOAN_NOC.CONFIRM_ADDRESS`
- address present and no `status`, user says yes -> `LOAN_NOC.CREATE_NOC_REQUEST`
- address present and no `status`, user says no -> `LOAN_NOC.SHOW_REDIRECTION`
- `status == "success"` -> `LOAN_NOC.SHOW_FINAL_STATUS`
- `status == "failure"` -> response only, preserve current fallback intent unless product changes it

Preserve strict confirmation: anything not explicitly yes is no.

### 11.2 PAY_CREDIT_CARD_BILL

Widget-driven graph. User text is help, cancel, or off-topic. Do not extract card, amount, or account from text in V1.

Graph:

```text
START
  -> merge_credit_card_inputs
  -> reset_credit_card_flags
  -> route_widget_resume_or_text
      -> request_card
      -> request_amount
      -> request_account
      -> prepare_confirmation
      -> classify_widget_help
      -> handle_widget_issue_or_abort
  -> END
```

Routing rules:

- first turn or `widget_response == "yes"` resumes widget progression
- missing `card_details` -> `PAY_CREDIT_CARD_BILL.SHOW_CREDIT_CARDS`
- missing `payment_amount` -> `PAY_CREDIT_CARD_BILL.SHOW_AMOUNT`
- missing `account_details` -> `PAY_CREDIT_CARD_BILL.SHOW_ACCOUNTS`
- all present -> `PAY_CREDIT_CARD_BILL.RAISE_FINAL_CONFIRMATION`
- typed `widget_issue` -> set `show_redirection = "yes"` and default journey intent unless the app adds a redirection intent
- typed abort -> empty intent
- repeated off-topic -> abort

### 11.3 EMAIL_UPDATE

Backend-callback graph with one confirmation classifier.

Graph:

```text
START
  -> merge_email_inputs
  -> reset_email_flags
  -> route_email_update
      -> request_eligibility
      -> show_not_eligible
      -> request_new_email
      -> raise_email_confirmation
      -> classify_email_confirmation
      -> request_email_mfa
      -> show_email_final_status
  -> END
```

Routing rules:

- `eligibility_checked == "no"` -> `EMAIL_UPDATE.CHANGE_EMAIL_ELIGIBILITY`
- `is_eligible == "no"` -> response only with default `EMAIL_UPDATE`
- eligible and missing `new_email` -> `EMAIL_UPDATE.VALIDATE_EMAIL`
- new email and confirmation not raised -> ask for confirmation, default `EMAIL_UPDATE`
- confirmation yes -> `EMAIL_UPDATE.MFA_EMAIL`
- confirmation no -> abort with empty intent
- ambiguous -> ask again, default `EMAIL_UPDATE`
- `status == "success"` -> `EMAIL_UPDATE.SHOW_FINAL_STATUS`, `abort = "yes"`
- `status == "failure"` -> final failure response, `abort = "yes"`

### 11.4 MOBILE_UPDATE

Use the email graph pattern, but do not copy the current implementation blindly. The current handler has known state mismatches:

- `handle()` references `self.default_state`, which is not initialized.
- `is_eligible` is stored as `"yes"` or `"no"` but checked with `is True` and `is False`.
- `get_intent_data()` calls `.lower()` on `status` even though initial status is `None`.
- `handle()` updates a local `state`, while `get_intent_data()` reads `self.state`.

V1 graph should use the intended product flow:

```text
START
  -> merge_mobile_inputs
  -> reset_mobile_flags
  -> route_mobile_update
      -> request_eligibility
      -> show_not_eligible
      -> request_new_mobile
      -> raise_mobile_confirmation
      -> classify_mobile_confirmation
      -> request_mobile_mfa
      -> show_mobile_final_status
  -> END
```

Routing rules should mirror email with these intents:

- `MOBILE_UPDATE.CHANGE_MOBILE_ELIGIBILITY`
- `MOBILE_UPDATE.VALIDATE_MOBILE`
- `MOBILE_UPDATE.MFA_MOBILE`
- `MOBILE_UPDATE.SHOW_FINAL_STATUS`

### 11.5 PAY_TO_MOBILE

Slot-filling plus widget callbacks.

Graph:

```text
START
  -> merge_upi_inputs
  -> reset_upi_flags
  -> maybe_classify_upi_control
  -> route_upi_control
  -> extract_payee_amount
  -> validate_upi_amount
  -> request_contact_selection
  -> request_account_selection
  -> prepare_upi_confirmation
  -> END
```

Routing rules:

- if `widget_response == "yes"`, skip LLM control classification for that turn
- abort -> empty intent
- first off-topic -> warning, default `PAY_TO_MOBILE`
- repeated off-topic -> abort
- missing or changed payee or amount -> structured extraction
- payee changed -> clear `registered_payee_details`
- invalid amount -> ask again, default `PAY_TO_MOBILE`
- valid payee and amount -> `PAY_TO_MOBILE.SHOW_CONTACT_LIST` with `payee_name`
- missing `registered_payee_details` -> `PAY_TO_MOBILE.SHOW_CONTACT_LIST`
- missing `account_details` -> `PAY_TO_MOBILE.SHOW_ACCOUNTS`
- all present -> `PAY_TO_MOBILE.RAISE_FINAL_CONFIRMATION` with `amount_to_be_paid`

### 11.6 OPEN_FD

Migrate last. It has the richest disambiguation and plan-selection logic.

Graph:

```text
START
  -> merge_fd_inputs
  -> reset_fd_flags
  -> classify_fd_control
  -> route_fd_control
  -> extract_fd_amount
  -> validate_fd_amount
  -> extract_fd_tenure
  -> select_fd_plan
  -> prepare_fd_confirmation
  -> END
```

Routing rules:

- abort -> empty intent
- `change_default` -> `Redirection`, intent `OPEN_FD`
- first off-topic -> warning
- repeated off-topic -> abort
- missing or changed amount -> extract and validate amount
- missing or changed tenure -> extract tenure and select plan
- no tenure or no matching plan -> `OPEN_FD.SHOW_PLANS`
- all required fields present -> `OPEN_FD.RAISE_FINAL_CONFIRMATION`

Important FD details to preserve:

- `expected_slot` disambiguates bare numbers.
- `consumed_value` prevents one bare number from being reused as both amount and tenure.
- Plan selection remains deterministic: matching tenure range, highest interest rate, then narrowest range.
- `change_amount_and_tenure` updates both slots from one user message.

## 12. Minimal Graph Skeleton

```python
from typing import Literal
from langgraph.graph import START, END, StateGraph


def route_loan_noc(state: LoanNocState) -> Literal[
    "request_loan_selection",
    "request_address_confirmation",
    "classify_address_confirmation",
    "show_final_status",
]:
    if not state.noc_loan:
        return "request_loan_selection"
    if not state.noc_address:
        return "request_address_confirmation"
    if state.status in {"success", "failure"}:
        return "show_final_status"
    return "classify_address_confirmation"


def build_loan_noc_graph():
    builder = StateGraph(LoanNocState)
    builder.add_node("merge_inputs", merge_loan_noc_inputs)
    builder.add_node("reset_flags", reset_loan_noc_flags)
    builder.add_node("request_loan_selection", request_loan_selection)
    builder.add_node("request_address_confirmation", request_address_confirmation)
    builder.add_node("classify_address_confirmation", classify_address_confirmation)
    builder.add_node("request_noc_creation", request_noc_creation)
    builder.add_node("show_redirection", show_redirection)
    builder.add_node("show_final_status", show_final_status)

    builder.add_edge(START, "merge_inputs")
    builder.add_edge("merge_inputs", "reset_flags")
    builder.add_conditional_edges("reset_flags", route_loan_noc)
    builder.add_conditional_edges(
        "classify_address_confirmation",
        route_after_address_confirmation,
        {
            "yes": "request_noc_creation",
            "no": "show_redirection",
        },
    )
    for node in [
        "request_loan_selection",
        "request_address_confirmation",
        "request_noc_creation",
        "show_redirection",
        "show_final_status",
    ]:
        builder.add_edge(node, END)

    return builder.compile()
```

For classifier nodes that both update state and choose the next node, `Command` is also acceptable. Use conditional edges when routing is simple and visible.

## 13. Soft Migration Sequence

`OPEN_FD` informed the reference conventions for complex slot-filling migrations. Keep those conventions documented in portable migration notes rather than relying on the migrated files as durable references.

Continue with one remaining handler at a time. A practical sequence is:

1. Add the `langgraph_intent_handlers/` package with shared `models/`, `utils/`, and empty `usecase_handlers/`.
2. Add `langgraph_rule_engine.py` with the same external process contract as `rule_engine.py`.
3. Add feature-flag or config-based engine selection while keeping FSM as the default.
4. Migrate `LOAN_NOC` into `langgraph_intent_handlers/usecase_handlers/loan_noc/`, following the `OPEN_FD` file structure where applicable.
5. Run parity tests against the FSM handler and enable LangGraph for `LOAN_NOC` only in lower environments.
6. Move `LOAN_NOC` through shadow mode, canary mode, and full-intent default only after observed parity.
7. Repeat the same pattern for `PAY_CREDIT_CARD_BILL`.
8. Repeat for `EMAIL_UPDATE`.
9. Repeat for `MOBILE_UPDATE` using the intended email-like flow, fixing the current state mismatches in the graph implementation rather than editing the FSM handler.
10. Repeat for `PAY_TO_MOBILE`.
11. Keep FSM handlers available until every migrated intent has enough production confidence and there is an explicit deprecation decision.

Each handler migration should be a small PR-sized change:

- add graph state model
- add node functions
- add graph builder
- add adapter tests
- add a migration analysis report with parity matrix
- add the handler to the LangGraph registry
- enable the intent through config only after parity is verified
- keep the legacy FSM handler as the rollback path

### 13.1 Migration Analysis Report

Every migrated handler should include a minimal report in:

```text
app/services/optimus_query_bot/fsm-langgraph-migration-report/<usecase_slug>_migration_analysis.md
```

Use lower snake_case for `<usecase_slug>` and align it with the target folder. The report should be short but concrete enough to catch missed functionality:

```markdown
# <INTENT> FSM To LangGraph Migration Analysis

## Scope

- Source FSM:
- Target LangGraph:
- Contract references:

## Overall Finding

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

## Remaining Risks

## Suggested Parity Scenarios

| Scenario | Input/State | Expected App Intent |
| --- | --- | --- |
```

Future migration reports should live under `app/services/optimus_query_bot/fsm-langgraph-migration-report/`.

## 14. Testing Checklist

For every migrated handler, test these levels:

- State model defaults validate and preserve expected legacy field names.
- `merge_inputs` correctly merges Redis state and app callback fields.
- `reset_turn_flags` clears only one-turn flags.
- Every app-facing intent from the legacy handler is still reachable.
- Abort returns `abort = "yes"` and empty intent where legacy behavior does.
- Widget callbacks skip text classification where legacy behavior does.
- Status success and failure produce the same final response category and abort behavior.
- `LangGraphRuleEngine` saves the same durable state keys as `RuleEngine`, excluding only `bot_response` and internal graph-only fields.
- Migration analysis report compares source and target behavior with a parity matrix.
- Engine selection defaults to FSM when an intent is not enabled for LangGraph.
- Engine selection can route one enabled intent to LangGraph without affecting other intents.
- Fallback to FSM is possible by config only, without code rollback.

Handler-specific regression cases:

- FD bare number while `expected_slot == "amount"`.
- FD bare number while `expected_slot == "tenure"`.
- FD amount larger than balance.
- FD tenure outside all plans.
- UPI payee change clears `registered_payee_details`.
- UPI app callback with `widget_response == "yes"` skips control classification.
- Credit card first turn requests card selection.
- Credit card widget callback advances from card to amount to account.
- Loan NOC ambiguous address confirmation routes to redirection.
- Email/mobile ambiguous confirmation asks again.
- Email/mobile success sets `abort = "yes"` after final status.

Additional soft-migration tests:

- Given the same `journey_state`, `journey_data`, `user_query`, and `additional_data`, FSM and LangGraph produce the same app-facing intent for parity cases.
- Graph state saved to Redis can be safely consumed by the FSM handler for that intent, or the rollout explicitly prevents mid-journey engine switching.
- Shadow mode never emits duplicate backend execution or widget side effects.
- Unknown or disabled graph intents return to FSM rather than failing production traffic.

## 15. V1 Acceptance Criteria

The V1 migration is complete when:

- All six current intent handlers are represented as LangGraph graphs.
- Existing FSM handlers still exist and remain callable.
- `LangGraphRuleEngine` can dispatch graph-backed handlers while preserving the existing response shape.
- A runtime selector or feature flag can choose FSM or LangGraph per intent.
- FSM remains the default for disabled or unknown graph intents.
- State schemas are Pydantic models with meaningful field descriptions.
- LLM calls use `ChatOpenAI` structured output through the shared client factory.
- Redis remains the source of journey state persistence.
- Existing app intent names and one-turn widget/backend handoffs remain compatible.
- Tests cover node-level routing and end-to-end per-turn outputs for every handler.
- Rollback from LangGraph to FSM is possible without reverting code.

## 16. Future Improvements After V1

Once parity is stable, consider:

- replacing legacy string flags with internal booleans plus an adapter
- adding LangGraph checkpointers for replay and debugging
- storing graph traces for customer support diagnostics
- extracting shared email/mobile flow into a parameterized graph factory
- replacing many UI flags with `next_action` only
- adding static diagrams generated from graph definitions
- deprecating FSM handlers only after a separate production-readiness decision
