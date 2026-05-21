# Handler Patterns

## Common FSM To Graph Patterns

Ordered guard clauses become conditional graph routing:

```text
if missing amount -> collect amount
elif missing tenure -> collect tenure
else -> confirmation
```

maps to:

```text
START -> merge_inputs -> reset_flags -> route_next
route_next -> collect_amount | collect_tenure | prepare_confirmation
```

One-turn UI flags become either resettable legacy fields or a normalized `next_action`. Keep legacy flags if they are needed for state parity or tests, but make `next_action` the primary app-facing output in the adapter.

LLM helpers are bounded classifiers/extractors. They should not execute business rules.

Widget/backend handoffs are per-turn terminal nodes. Emit the app action, end the graph invocation, and wait for `additional_data` on the next request.

## LOAN_NOC

Primary durable state:

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

Routing:

- missing `noc_loan` -> `LOAN_NOC.SELECT_NOC_LOAN`
- missing `noc_address` -> `LOAN_NOC.CONFIRM_ADDRESS`
- address present and no `status`, user confirms -> `LOAN_NOC.CREATE_NOC_REQUEST`
- address present and no `status`, user rejects or is ambiguous -> `LOAN_NOC.SHOW_REDIRECTION`
- `status == "success"` -> `LOAN_NOC.SHOW_FINAL_STATUS`, include `service_request_no`
- `status == "failure"` -> failure response, preserve legacy abort/intent category unless product changes it

## PAY_CREDIT_CARD_BILL

Primary durable state:

```text
card_details
payment_amount
account_details
fetch_card_details
fetch_payment_amount
fetch_account_details
raise_final_confirmation
widget_response
show_redirection
abort
off_topic_count
count
```

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

Rules:

- first turn or `widget_response == "yes"` resumes widget progression
- missing `card_details` -> `PAY_CREDIT_CARD_BILL.SHOW_CREDIT_CARDS`
- missing `payment_amount` -> `PAY_CREDIT_CARD_BILL.SHOW_AMOUNT`
- missing `account_details` -> `PAY_CREDIT_CARD_BILL.SHOW_ACCOUNTS`
- all present -> `PAY_CREDIT_CARD_BILL.RAISE_FINAL_CONFIRMATION`
- typed widget issue -> redirection/default journey behavior
- typed abort -> empty intent and abort
- repeated off-topic -> abort
- do not extract card, amount, or account from text in V1

## EMAIL_UPDATE

Primary durable state:

```text
change_email_eligibility
eligibility_checked
is_eligible
current_email
new_email
get_new_email
confirmation_raised
email_mfa
status
service_request_no
abort
```

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

Rules:

- `eligibility_checked == "no"` -> `EMAIL_UPDATE.CHANGE_EMAIL_ELIGIBILITY`
- `is_eligible == "no"` -> response only with default `EMAIL_UPDATE`
- eligible and missing `new_email` -> `EMAIL_UPDATE.VALIDATE_EMAIL`
- new email and confirmation not raised -> ask for confirmation with default `EMAIL_UPDATE`
- confirmation yes -> `EMAIL_UPDATE.MFA_EMAIL`
- confirmation no -> abort and empty intent
- ambiguous -> ask again with default `EMAIL_UPDATE`
- `status == "success"` -> `EMAIL_UPDATE.SHOW_FINAL_STATUS`, `abort = "yes"`
- `status == "failure"` -> final failure response, `abort = "yes"`

## MOBILE_UPDATE

Use the intended email-like flow, but do not blindly copy the current FSM implementation. Known source issues:

- `handle()` references `self.default_state`, while `__init__` defines `self.state`.
- `is_eligible` is normalized to string but compared to booleans in places.
- `get_intent_data()` can call `.lower()` on `None` status.
- `handle()` updates a local state while `get_intent_data()` reads `self.state`.

Graph intents:

```text
MOBILE_UPDATE.CHANGE_MOBILE_ELIGIBILITY
MOBILE_UPDATE.VALIDATE_MOBILE
MOBILE_UPDATE.MFA_MOBILE
MOBILE_UPDATE.SHOW_FINAL_STATUS
```

Mirror email update with mobile fields:

```text
current_mobile
new_mobile
get_new_mobile
mobile_mfa
```

## PAY_TO_MOBILE

Primary durable state:

```text
payee_name
amount_to_be_paid
registered_payee_details
account_details
show_contact_list
fetch_account_details
request_to_proceed
widget_response
abort
off_topic_count
```

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

Rules:

- if `widget_response == "yes"`, skip LLM control classification
- abort -> empty intent
- first off-topic -> warning/default `PAY_TO_MOBILE`
- repeated off-topic -> abort
- missing or changed payee/amount -> structured extraction
- payee changed -> clear `registered_payee_details`
- invalid amount or amount greater than `primary_balance` -> ask again
- valid payee and amount -> `PAY_TO_MOBILE.SHOW_CONTACT_LIST` with `payee_name`
- missing `registered_payee_details` -> `PAY_TO_MOBILE.SHOW_CONTACT_LIST`
- missing `account_details` -> `PAY_TO_MOBILE.SHOW_ACCOUNTS`
- all present -> `PAY_TO_MOBILE.RAISE_FINAL_CONFIRMATION`

## OPEN_FD

Primary durable state:

```text
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
```

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

Rules:

- abort -> empty intent
- `change_default` -> `Redirection`, intent `OPEN_FD`
- first off-topic -> warning/default journey
- repeated off-topic -> abort
- missing or changed amount -> extract and validate amount
- missing or changed tenure -> extract tenure and select plan
- no tenure or no matching plan -> `OPEN_FD.SHOW_PLANS`
- all required fields present -> `OPEN_FD.RAISE_FINAL_CONFIRMATION`

Important details to preserve:

- `expected_slot` disambiguates bare numbers.
- `consumed_value` prevents reusing one bare number as both amount and tenure.
- Plan selection is deterministic: matching tenure range, highest interest rate, then narrowest range.
- `change_amount_and_tenure` updates both slots from one message.
