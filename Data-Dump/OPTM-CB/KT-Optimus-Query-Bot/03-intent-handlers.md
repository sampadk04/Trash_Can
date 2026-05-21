# Intent Handlers

## Supported Journeys

`RuleEngine` maps these `journey_name` / `intent_type` values to handlers:

```text
OPEN_FD                -> FixedDepositHandler
PAY_CREDIT_CARD_BILL  -> CreditCardHandler
PAY_TO_MOBILE         -> UPIHandler
LOAN_NOC              -> LoanNocHandler
EMAIL_UPDATE          -> EmailChangeHandler
MOBILE_UPDATE         -> MobileChangeHandler
```

The handler contract is:

```text
1. Load prior state from Redis.
2. Merge any app-provided additional_data.
3. Inspect the current user query.
4. Set bot_response and one or more control flags.
5. Return state.
6. RuleEngine maps flags to app-facing intent names.
```

## OPEN_FD

Primary state:

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

Flow:

```text
Start OPEN_FD
  |
  v
Need amount?
  |
  +-- yes -> LLM extracts amount
  |          validate min/max/current balance
  |          if missing/invalid: expected_slot = amount
  |
  v
Need tenure?
  |
  +-- yes -> LLM extracts tenure using expected_slot
  |          if missing: show_interest_rate_chart = true
  |          if provided: select best plan by tenure and rate
  |
  v
Raise final confirmation
```

App-facing intents:

```text
OPEN_FD.SHOW_PLANS
OPEN_FD.RAISE_FINAL_CONFIRMATION
OPEN_FD
```

Important details:

```text
Bare number handling is explicit.

If bot asked for amount:
  "5000" means amount.

If bot asked for tenure:
  "500" means 500 days.

If user gives units:
  "50k for 6 months" overrides expected_slot and updates both fields.
```

## PAY_CREDIT_CARD_BILL

Primary state:

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

Flow:

```text
Start CC payment
  |
  v
Need card_details?      -> ask app to show credit cards
  |
  v
Need payment_amount?    -> ask app to show payment amount options
  |
  v
Need account_details?   -> ask app to show accounts
  |
  v
Raise final confirmation
```

App-facing intents:

```text
PAY_CREDIT_CARD_BILL.SHOW_CREDIT_CARDS
PAY_CREDIT_CARD_BILL.SHOW_AMOUNT
PAY_CREDIT_CARD_BILL.SHOW_ACCOUNTS
PAY_CREDIT_CARD_BILL.RAISE_FINAL_CONFIRMATION
```

Important detail:

```text
This journey is widget-driven. The user is expected to select from UI controls.
If the user types instead, the LLM helper classifies widget issue / abort / other.
```

## PAY_TO_MOBILE

Primary state:

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

Flow:

```text
Start UPI payment
  |
  v
Extract payee + amount from user query
  |
  +-- missing payee/amount -> ask for missing field
  |
  +-- amount > balance -> ask for valid amount
  |
  v
show_contact_list = yes
  |
  | app returns registered_payee_details
  v
Need account_details?
  |
  +-- yes -> fetch_account_details = yes
  |
  v
request_to_proceed = yes
  |
  v
Raise final confirmation
```

App-facing intents:

```text
PAY_TO_MOBILE.SHOW_CONTACT_LIST
PAY_TO_MOBILE.SHOW_ACCOUNTS
PAY_TO_MOBILE.RAISE_FINAL_CONFIRMATION
```

Important details:

```text
Changing payee invalidates registered_payee_details.
The handler validates amount against primary_balance.
For non-widget text, an LLM classifier distinguishes change_payee_or_amount, abort, other, none.
```

## LOAN_NOC

Primary state:

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
Start LOAN_NOC
  |
  v
Need noc_loan?       -> fetch_loan_list = yes
  |
  v
Need noc_address?    -> show_address = yes
  |
  v
User confirms address?
  |
  +-- yes -> raise_noc_request = yes
  |
  +-- no  -> show_redirection = yes
  |
  v
App sets status success/failure
  |
  v
Show final status
```

App-facing intents:

```text
LOAN_NOC.SELECT_NOC_LOAN
LOAN_NOC.CONFIRM_ADDRESS
LOAN_NOC.CREATE_NOC_REQUEST
LOAN_NOC.SHOW_REDIRECTION
LOAN_NOC.SHOW_FINAL_STATUS
```

## EMAIL_UPDATE

Primary state:

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

Flow:

```text
Start EMAIL_UPDATE
  |
  v
Check eligibility        -> CHANGE_EMAIL_ELIGIBILITY
  |
  | app returns is_eligible + current_email
  v
Eligible?
  |
  +-- no  -> tell user not eligible
  |
  +-- yes -> get_new_email = yes
             app validates/provides new_email
  |
  v
Raise confirmation
  |
  +-- yes -> email_mfa = yes
  +-- no  -> abort
  |
  v
App returns status + service_request_no
  |
  v
Show final status
```

App-facing intents:

```text
EMAIL_UPDATE.CHANGE_EMAIL_ELIGIBILITY
EMAIL_UPDATE.VALIDATE_EMAIL
EMAIL_UPDATE.MFA_EMAIL
EMAIL_UPDATE.SHOW_FINAL_STATUS
```

## MOBILE_UPDATE

Primary state:

```text
change_mobile_eligibility
eligibility_checked
is_eligible
current_mobile
new_mobile
get_new_mobile
confirmation_raised
mobile_mfa
status
service_request_no
abort
```

Expected flow mirrors email update:

```text
Start MOBILE_UPDATE
  |
  v
Check eligibility        -> CHANGE_MOBILE_ELIGIBILITY
  |
  | app returns is_eligible + current_mobile
  v
Collect new_mobile       -> VALIDATE_MOBILE
  |
  v
Raise confirmation
  |
  +-- yes -> MFA_MOBILE
  +-- no  -> abort
  |
  v
Show final status
```

App-facing intents:

```text
MOBILE_UPDATE.CHANGE_MOBILE_ELIGIBILITY
MOBILE_UPDATE.VALIDATE_MOBILE
MOBILE_UPDATE.MFA_MOBILE
MOBILE_UPDATE.SHOW_FINAL_STATUS
```

Code note:

```text
The current mobile handler appears to reference self.default_state inside handle(),
but __init__ defines self.state only. Also, additional_data converts is_eligible
to a lowercase string, while handle compares it to booleans in a few places.
This should be reviewed before relying on MOBILE_UPDATE in production.
```

## How To Add A New Journey

At a high level:

```text
1. Add an intent record to the Redis search/index data with:
   intent, label, intent_type, line_of_business, deeplink, FAQ text/embeddings.

2. Create a new handler in intent_handlers/.

3. Add the mapping in RuleEngine.handler_classes.

4. Add required journey-data keys in RuleEngine.INTENT_REQUIRED_KEYS if needed.

5. Add the journey name to SUPPORTED_JOURNEYS in the route.

6. Ensure the app understands returned intent names and additional_data.
```

