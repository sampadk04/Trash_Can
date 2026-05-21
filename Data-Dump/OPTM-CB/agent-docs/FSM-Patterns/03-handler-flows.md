# Handler Flows

## OPEN_FD

Source: `app/services/optimus_query_bot/intent_handlers/fixed_deposit.py`

State:

```text
fd_amount
tenure
tenure_description
interest_rate
show_interest_rate_chart
raise_final_confirmation
abort
change_default
off_topic_count
tenure_info
expected_slot
```

Flow:

```text
START
  |
  v
classify current text intent
  |
  +-- abort          -> abort journey
  +-- change_default -> redirection
  +-- other          -> warn once, abort after repeated off-topic
  |
  v
need amount or changing amount?
  |
  +-- yes -> LLM extract fd_amount
            validate min amount, max amount, current balance
            missing/invalid -> expected_slot = amount, ask again
  |
  v
need tenure or changing tenure?
  |
  +-- yes -> LLM extract tenure using rate card, consumed amount, expected_slot
            no tenure -> expected_slot = tenure, show_interest_rate_chart = true
            no matching plan -> show_interest_rate_chart = true
            matching plan -> set interest_rate/product/tenure_info fields
  |
  v
raise final confirmation
```

App-facing intents:

```text
OPEN_FD.SHOW_PLANS
OPEN_FD.RAISE_FINAL_CONFIRMATION
OPEN_FD
```

Key design points:

- `expected_slot` disambiguates bare numbers. If the bot asked for amount, `"5000"` means amount. If it asked for tenure, `"500"` means days.
- `consumed_value` prevents the same bare number from being used as both amount and tenure in one message.
- FD plan selection is deterministic once tenure is known: choose matching plans, sort by highest interest rate, then tighter tenure range.
- `change_amount_and_tenure` lets one user message update both slots.

LangGraph shape:

```text
reset_flags
  -> classify_fd_control
  -> route_control
  -> collect_or_update_amount
  -> validate_amount
  -> collect_or_update_tenure
  -> select_plan
  -> prepare_fd_confirmation
  -> emit_action
```

## PAY_TO_MOBILE

Source: `app/services/optimus_query_bot/intent_handlers/upi.py`

State:

```text
payee_name
amount_to_be_paid
registered_payee_details
show_contact_list
fetch_account_details
account_details
request_to_proceed
abort
off_topic_count
widget_response
```

Flow:

```text
START
  |
  v
reset UI flags
  |
  v
if user text is not app widget callback:
  classify journey intent
    +-- abort -> abort
    +-- other -> warn once, abort after repeated off-topic
    +-- change_payee_or_amount -> re-enter extraction
  |
  v
missing payee or amount, or user changed either?
  |
  +-- yes -> LLM extract payee and amount
            missing payee/amount -> ask only for missing value
            payee changed -> clear registered_payee_details
            validate amount against balance
            valid -> show_contact_list = yes
  |
  v
missing registered_payee_details?
  |
  +-- yes -> show_contact_list = yes
  |
  v
missing account_details?
  |
  +-- yes -> fetch_account_details = yes
  |
  v
raise final payment confirmation
```

App-facing intents:

```text
PAY_TO_MOBILE.SHOW_CONTACT_LIST
PAY_TO_MOBILE.SHOW_ACCOUNTS
PAY_TO_MOBILE.RAISE_FINAL_CONFIRMATION
PAY_TO_MOBILE
```

Key design points:

- `widget_response == yes` skips LLM control classification for that turn because the app callback is trusted as state input.
- Payee changes invalidate selected payee details.
- Contact selection and account selection are external app interactions.
- Amount validation is local and uses `journey_data.primary_balance`.

LangGraph shape:

```text
merge_widget_callback
  -> reset_flags
  -> maybe_classify_upi_control
  -> route_control
  -> extract_payee_amount
  -> validate_upi_amount
  -> request_contact_selection
  -> request_account_selection
  -> prepare_upi_confirmation
```

## PAY_CREDIT_CARD_BILL

Source: `app/services/optimus_query_bot/intent_handlers/credit_card.py`

State:

```text
card_details
payment_amount
account_details
fetch_card_details
fetch_payment_amount
fetch_account_details
raise_final_confirmation
abort
off_topic_count
show_redirection
count
widget_response
```

Flow:

```text
START
  |
  v
reset UI flags, increment count
  |
  v
if first turn or app widget callback:
  missing card_details?    -> fetch_card_details = yes
  missing payment_amount?  -> fetch_payment_amount = yes
  missing account_details? -> fetch_account_details = yes
  otherwise                -> raise_final_confirmation = yes
  |
  v
if user typed during widget flow:
  LLM get_help
    +-- widget_issue -> show_redirection = yes
    +-- abort        -> abort
    +-- other        -> warn once, abort on repeated off-topic
```

App-facing intents:

```text
PAY_CREDIT_CARD_BILL.SHOW_CREDIT_CARDS
PAY_CREDIT_CARD_BILL.SHOW_AMOUNT
PAY_CREDIT_CARD_BILL.SHOW_ACCOUNTS
PAY_CREDIT_CARD_BILL.RAISE_FINAL_CONFIRMATION
PAY_CREDIT_CARD_BILL
```

Key design points:

- This is the most widget-driven flow. Text input is treated mostly as help/off-topic/cancel, not as slot data.
- `count` separates the initial widget prompt from later typed user queries.
- `widget_response` lets app callbacks resume normal progression.

LangGraph shape:

```text
reset_flags
  -> route_widget_resume_or_text_help
  -> request_card | request_amount | request_account | prepare_cc_confirmation
  -> emit_action
```

## LOAN_NOC

Source: `app/services/optimus_query_bot/intent_handlers/loan_noc.py`

State:

```text
noc_loan
noc_address
status
service_request_no
fetch_loan_list
show_address
raise_noc_request
show_redirection
abort
```

Flow:

```text
START
  |
  v
reset UI flags
  |
  v
missing noc_loan?
  +-- yes -> fetch_loan_list = yes
  |
  v
missing noc_address?
  +-- yes -> show_address = yes
  |
  v
address known and status missing?
  +-- user confirms yes -> raise_noc_request = yes
  +-- user confirms no  -> show_redirection = yes
  |
  v
status success? -> final success response
status failure? -> final failure response
```

App-facing intents:

```text
LOAN_NOC.SELECT_NOC_LOAN
LOAN_NOC.CONFIRM_ADDRESS
LOAN_NOC.SHOW_REDIRECTION
LOAN_NOC.CREATE_NOC_REQUEST
LOAN_NOC.SHOW_FINAL_STATUS
LOAN_NOC
```

Key design points:

- The confirmation classifier is intentionally strict: anything not explicitly yes becomes no.
- Creating the NOC request is external. Handler emits `CREATE_NOC_REQUEST`; later app/backend sends `status` and `service_request_no`.
- `show_redirection` exists in runtime state but is not part of `initialize_noc_state`; it is added dynamically.

LangGraph shape:

```text
reset_flags
  -> request_loan_selection
  -> request_address_confirmation
  -> classify_address_confirmation
  -> create_noc_request_or_redirect
  -> show_final_status
```

## EMAIL_UPDATE

Source: `app/services/optimus_query_bot/intent_handlers/email_update.py`

State:

```text
change_email_eligibility
eligibility_checked
is_eligible
email_mfa
get_new_email
new_email
current_email
service_request_no
confirmation_raised
status
abort
off_topic_count
```

Flow:

```text
START
  |
  v
reset UI flags
  |
  v
eligibility not checked?
  +-- yes -> change_email_eligibility = yes
  |
  v
not eligible?
  +-- yes -> tell user not eligible
  |
  v
eligible but missing new_email?
  +-- yes -> get_new_email = yes
  |
  v
new_email present and confirmation not raised?
  +-- yes -> confirmation_raised = yes, ask user to confirm
  |
  v
confirmation raised and status none?
  +-- yes -> LLM classify yes/no/ambiguous
            yes -> email_mfa = yes
            no  -> abort = yes
            ambiguous -> ask again
  |
  v
status success/failure -> final response, abort = yes
```

App-facing intents:

```text
EMAIL_UPDATE.CHANGE_EMAIL_ELIGIBILITY
EMAIL_UPDATE.VALIDATE_EMAIL
EMAIL_UPDATE.MFA_EMAIL
EMAIL_UPDATE.SHOW_FINAL_STATUS
EMAIL_UPDATE
```

Key design points:

- Eligibility check, email validation, MFA, and final service request creation are app/backend-owned.
- Handler owns the confirmation step between collecting email and asking for MFA.
- Status success/failure terminates with `abort = yes`, which is used as "journey finished" as well as "cancelled".

LangGraph shape:

```text
reset_flags
  -> request_eligibility
  -> route_eligibility
  -> request_new_email
  -> raise_email_confirmation
  -> classify_confirmation
  -> request_email_mfa
  -> show_final_status
```

## MOBILE_UPDATE

Source: `app/services/optimus_query_bot/intent_handlers/mobile_no_update.py`

Intended state:

```text
change_mobile_eligibility
eligibility_checked
is_eligible
get_new_mobile
mobile_mfa
current_mobile
new_mobile
service_request_no
confirmation_raised
status
abort
off_topic_count
```

Intended flow mirrors `EMAIL_UPDATE`:

```text
eligibility check
  -> not eligible or collect new mobile
  -> raise confirmation
  -> classify yes/no/ambiguous
  -> yes triggers mobile_mfa
  -> no aborts
  -> service_request_no/status creates final response
```

App-facing intents:

```text
MOBILE_UPDATE.CHANGE_MOBILE_ELIGIBILITY
MOBILE_UPDATE.VALIDATE_MOBILE
MOBILE_UPDATE.MFA_MOBILE
MOBILE_UPDATE.SHOW_FINAL_STATUS
MOBILE_UPDATE
```

Observed implementation risks to preserve awareness during migration:

- `handle()` references `self.default_state`, but the class only initializes `self.state`.
- `_update_state_from_request()` stores `is_eligible` as lower-case string, while `handle()` checks `is True` and `is False`.
- `get_intent_data()` calls `.lower()` on `status`; initial status is `None`.
- The flow uses a local `state` variable in `handle()`, but `get_intent_data()` reads `self.state`, which may not contain returned updates.

For LangGraph migration, treat mobile update as the same product pattern as email update, but verify/fix these behavioral mismatches before using it as a source-of-truth implementation.
