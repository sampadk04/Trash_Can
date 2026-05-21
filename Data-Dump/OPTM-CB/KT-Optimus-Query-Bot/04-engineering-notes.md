# Engineering Notes

## Runtime Dependencies

The service depends on these major systems:

```text
Redis / RedisVL
  - FAQ/action search index
  - session state
  - journey FSM state
  - short conversation history

LLM Gateway
  - general intent routing
  - query rewriting
  - slot extraction and confirmation classifiers

Embedding service
  - financial embeddings for vector retrieval

Kafka
  - conversation event logging

Deepgram
  - audio transcription endpoint

PII masking service
  - masks user query before processing in converse route

Tracing and metrics
  - @traced spans
  - ApiLatencyTracker
  - Prometheus endpoint
```

## Redis Keys

```text
session:{ai_session_id}
  Main journey/session hash.
  TTL: 86400 seconds on initialization.

intent:{intent_id}:{journey_name}_state
  Per-journey FSM hash.
  TTL: 1800 seconds.

intent:{intent_id}:history
  Recent conversation turns.
  TTL: 86400 seconds.
```

## Important Session Fields

`StateManager.initialize_journey()` stores app-provided customer context and derived flags:

```text
ai_session_id
session_id
intent_id
journey_name
customer_id
primary_balance
language
search_type
customer_profile
customer_type
role
residential_status
loans
credit_card
debit_card
account
deposits
fixed_deposit_plans
has_savings_account
has_credit_card
has_loan
has_fasttag
has_fd
additional_data
```

Most list/dict fields are JSON-encoded before writing to Redis and decoded on read.

## Response Contract

The converse endpoint returns:

```text
{
  ai_session_id: "...",
  intent_id: "...",
  response: "Text shown to user",
  missing_data: [],
  intent_list: [
    {
      intent: "OPEN_FD.SHOW_PLANS",
      label: "...",
      intent_type: "Clarification",
      deeplink: "..."
    }
  ],
  additional_data: {
    ...latest saved FSM state...
  }
}
```

The `intent_list` is how the app knows whether to show a widget, redirect, trigger an execution API, or ask for confirmation.

## LLM Gateway Usage

All LLM calls go through `app/clients/llm_gw.py`.

```text
LLMGatewayClient
  |
  +-- gets auth token from LLMGW_AUTH_URL
  +-- caches token until near expiry
  +-- posts model payload to LLMGW_MODEL_URL
  +-- retries once on 401 by refreshing token
```

The default model in this service is `gpt-5.4`, with:

```text
temperature: 0.0
top_p: 0.9
max_completion_tokens: 1024
```

Most calls use a strict JSON schema response format. This is important because handlers parse the LLM output directly with `json.loads()`.

## Observability

Useful observability hooks:

```text
@traced()
  Applied to service, retrieval, state-manager, and LLM-gateway methods.

add_span_attribute("ai_session_id", ...)
  Adds session id to request tracing.

ApiLatencyTracker
  Records endpoint latency by APIUseCase and HTTP method.

log_usage(response, context)
  Logs token usage when the LLM gateway response includes usage metadata.

Kafka conversation logging
  add_conversation_turn() pushes user_query and bot_response to configured Kafka topic.
```

## Security And Safety Guardrails

The bot has several safety boundaries:

```text
PII masking:
  User query is masked at the route before downstream handling.

Restricted router prompt:
  The general LLM prompt tells the model to choose only eligible intent IDs,
  reject off-domain/injection queries, and avoid revealing system details.

Structured output:
  JSON schema limits router and slot-extraction outputs.

Eligibility check:
  Retrieved intents are filtered by customer line of business before the LLM
  can return them as actionable options.
```

## Known Maintenance Notes

These are worth checking before major changes:

```text
1. MOBILE_UPDATE handler looks inconsistent.
   It references self.default_state, which is not initialized in __init__.
   It also mixes string values such as "yes"/"no" with boolean comparisons.

2. skip_llm path in the route calls add_conversation_turn without ai_session_id.
   StateManager.add_conversation_turn requires ai_session_id, intent_id,
   user_query, and bot_response.

3. Some handlers instantiate stateful classes per request through RuleEngine,
   then persist only the returned state. This is fine, but all durable state must
   be in the returned dictionary.

4. User-facing responses mix Markdown and HTML tags.
   The query-rewrite prompt explicitly says HTML responses are valid, so UI
   rendering should be designed for both formats.

5. The retrieval module is named retrival.py.
   Keep imports consistent unless doing a deliberate rename across the codebase.
```

## Development Checklist

When changing or adding a journey:

```text
[ ] Confirm app contract: what widget/action intent names will the app handle?
[ ] Define durable FSM state fields.
[ ] Decide what comes from user text vs app additional_data.
[ ] Keep LLM calls narrow and schema-constrained.
[ ] Reset transient UI flags every turn.
[ ] Set abort = "yes" only when the route should clear active journey fields.
[ ] Save enough additional_data for the app to render the next step.
[ ] Add eligibility and required-data checks in RuleEngine if needed.
[ ] Test at least: happy path, missing data, invalid data, abort, off-topic input.
```

