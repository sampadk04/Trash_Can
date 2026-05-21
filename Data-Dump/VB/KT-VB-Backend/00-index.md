# Jarvis Voice Bot Backend KT

This KT pack explains the Jarvis Voice Bot backend at an architecture level, with emphasis on the ML conversation loop, prompt-driven FSM behavior, websocket audio transport, and persistence/integration points.

Read in this order:

1. [01-system-architecture.md](01-system-architecture.md) - high-level runtime architecture and important directories.
2. [02-core-ml-and-fsm-flow.md](02-core-ml-and-fsm-flow.md) - STT -> LLM -> tools/FSM -> TTS flow, prompts, models, and node transitions.
3. [03-websocket-and-audio-flow.md](03-websocket-and-audio-flow.md) - how telephony/browser websocket sessions are established and how audio moves both ways.
4. [04-data-and-integrations.md](04-data-and-integrations.md) - Redis config lookup, Kafka conversation logging, external banking APIs, and usecase-specific side effects.

## One-screen summary

Jarvis is a FastAPI websocket service. For each call, it:

Client/Telephony websocket
-> `main.py` accepts `/connect_call_airtel`
-> loads call config from Redis or mock input
-> chooses usecase flow nodes, prompt, LLM model, STT, TTS, and action factory
-> creates `AirtelPhoneConversation` or `NexusPhoneConversation`
-> streams inbound audio to STT
-> sends final transcripts to `ChatGPTAgent`
-> streams LLM responses to TTS
-> sends synthesized audio chunks back on websocket
-> runs tools/actions that can update state, call APIs, switch nodes, or terminate
-> logs final conversation payload to Kafka.

The central orchestration class is `vocode/streaming/streaming_conversation.py`. Bank-specific behavior lives mostly in:

- `flows/` - node/state definitions.
- `prompts/` - prompt templates by usecase, language, and speaker gender.
- `vocode/streaming/action/` - LLM-callable tools and action factories.
- `vocode/streaming/usecase_handler/` - extra prompt rendering and node-switch processing for selected usecases.
- `vocode/streaming/*_helper.py` - usecase API helpers and business logic.

