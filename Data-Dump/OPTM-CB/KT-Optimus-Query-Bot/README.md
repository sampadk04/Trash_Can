# Optimus Query Bot KT

This folder is a knowledge-transfer guide for the Optimus Query Bot backend.
It focuses on the service code under:

`optimus-app-services/app/services/optimus_query_bot`

Use these files in order:

1. [01-system-overview.md](01-system-overview.md) - what the bot is, where it sits, and the end-to-end request path.
2. [02-ml-and-fsm-flow.md](02-ml-and-fsm-flow.md) - the core ML routing and finite-state journey logic.
3. [03-intent-handlers.md](03-intent-handlers.md) - supported journeys and the important state variables for each.
4. [04-engineering-notes.md](04-engineering-notes.md) - integrations, storage, observability, and maintenance notes.

The short version:

```text
Mobile App
  |
  | init-journey: sends customer context and product holdings
  v
Redis session state
  |
  | converse: user asks a banking question
  v
Query Bot service
  |
  +-- No active journey:
  |     Spell correction -> exact/BM25/vector retrieval -> LOB eligibility -> LLM router
  |
  +-- Active journey:
        RuleEngine -> intent-specific handler -> state update -> app UI action
```

The design is intentionally narrow. The general bot does not try to be a fully open-ended assistant. It retrieves eligible banking actions/information, lets the LLM pick from that constrained set, and hands supported execution journeys to deterministic state-machine handlers.

