# FSM Patterns

This folder captures how the current Optimus Query Bot intent handlers work today, with emphasis on the reusable FSM patterns that should guide a LangGraph migration.

Read in this order:

1. [01-runtime-contract.md](01-runtime-contract.md) - how `RuleEngine`, Redis state, handlers, app widgets, and `additional_data` interact.
2. [02-common-fsm-patterns.md](02-common-fsm-patterns.md) - repeated design motifs across handlers.
3. [03-handler-flows.md](03-handler-flows.md) - per-handler state, transitions, app-facing intents, and edge cases.
4. [04-langgraph-migration-map.md](04-langgraph-migration-map.md) - how the current FSM shapes map to LangGraph nodes, state, edges, and interrupts.

Scope covered:

- `app/services/optimus_query_bot/rule_engine.py`
- `app/services/optimus_query_bot/intent_handlers/*.py`

The rest of the chatbot stack is referenced only where needed to explain how handlers are invoked and persisted.
