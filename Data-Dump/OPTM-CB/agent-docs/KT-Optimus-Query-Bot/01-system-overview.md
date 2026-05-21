# System Overview

## Purpose

Optimus Query Bot is a backend service for the Optimus App. It helps users with narrow, app-supported banking tasks such as opening an FD, paying a credit card bill, paying via UPI, updating email/mobile, and raising a loan NOC request.

The bot has two main modes:

```text
1. General query routing
   User asks: "I want to open an FD"
   Bot finds matching available actions and responses.

2. Active journey handling
   User is already inside OPEN_FD / PAY_TO_MOBILE / etc.
   Bot advances that journey using saved state and app-provided widget data.
```

## Important Code Locations

```text
app/routes/optimus_query_bot.py
  FastAPI routes, request/response models, session initialization, converse endpoint.

app/services/optimus_query_bot/query_bot.py
  Main service facade. Handles retrieval, LLM routing, eligibility checks, query rewriting,
  and delegates active journeys to RuleEngine.

app/services/optimus_query_bot/rule_engine.py
  Maps journey/intent types to handler classes and persists handler state.

app/services/optimus_query_bot/state_manager.py
  Redis-backed session, journey-state, and short conversation history storage.

app/services/optimus_query_bot/retrival.py
  RedisVL FAQ/action retrieval using exact tag search, BM25, and vector search.

app/services/optimus_query_bot/intent_handlers/
  One handler per supported execution journey.

app/clients/llm_gw.py
  LLM Gateway client with auth-token handling and structured response schema.
```

## Public API Shape

The key endpoints are:

```text
POST /optimus-query-bot/init-journey
  Creates ai_session_id and stores customer context in Redis.

POST /optimus-query-bot/converse
  Main chat endpoint. Either routes a query or continues an active journey.

POST /optimus-query-bot/transcribe
  Converts audio to text using Deepgram.

GET /api/v1/metrics
  Prometheus metrics endpoint.
```

## End-to-End Request Flow

```text
App calls init-journey
  |
  v
StateManager.initialize_journey()
  - Stores customer profile and product holdings in Redis
  - Computes convenience flags such as has_credit_card, has_loan, has_fd
  |
  v
App calls converse with ai_session_id + query
  |
  v
Route masks PII in query
  |
  v
StateManager.get_journey_data(ai_session_id)
  |
  +-- If session missing:
  |     return 404
  |
  +-- If journey_name is empty:
  |     run general query routing
  |
  +-- If journey_name is present:
        run intent-specific FSM handler
```

## General Query Routing

When no journey is active, `QueryBotService.generate_response()` performs:

```text
Raw user query
  |
  v
Spell correction
  |
  v
Exact tag search for short queries
  |
  +-- Single exact match:
  |     Check customer line-of-business eligibility
  |     Return deterministic response
  |
  +-- No exact match:
        BM25 search + vector search
          |
          v
        Weighted fusion
          |
          v
        Split into eligible and non-eligible intents
          |
          v
        LLM router selects only eligible IDs
          |
          v
        Return message + intent list
```

If exactly one returned intent maps to a supported journey, the route starts a new journey by setting:

```text
session:{ai_session_id}
  intent_id    = new UUID
  journey_name = selected journey, e.g. OPEN_FD
```

Then the same request is passed into that journey handler.

## Active Journey Handling

When `journey_name` is already set, routing skips general retrieval and goes straight to:

```text
converse route
  |
  v
QueryBotService.intent_handler()
  |
  v
RuleEngine.process_intent()
  |
  v
Load journey-specific state from Redis
  |
  v
Merge app-provided additional_data into handler state
  |
  v
Handler.handle()
  |
  v
Save updated state
  |
  v
Return bot_response + intent_list + additional_data
```

The app uses returned intent/action names such as `OPEN_FD.SHOW_PLANS` or `PAY_TO_MOBILE.SHOW_CONTACT_LIST` to render widgets or trigger downstream APIs.

