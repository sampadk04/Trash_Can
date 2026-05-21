# System Architecture

## Runtime shape

Jarvis is a FastAPI backend that hosts a long-lived websocket per live voice call. The codebase is built around a modified Vocode streaming architecture, with additional bank-specific layers for prompts, usecases, actions, telephony providers, and post-call logging.

Simple runtime flow:

```text
┌──────────────────────────┐
│ Telephony / browser      │
│ websocket client         │
└─────────────┬────────────┘
              │
              v
┌──────────────────────────┐
│ FastAPI main.py          │
│ /connect_call_airtel     │
└─────────────┬────────────┘
              │
              v
┌──────────────────────────┐
│ Call bootstrap           │
│ - parse metadata         │
│ - load Redis/mock config │
│ - choose usecase         │
│ - choose nodes/prompts   │
│ - choose STT/LLM/TTS     │
└─────────────┬────────────┘
              │
              v
┌──────────────────────────┐
│ StreamingConversation    │
│ workers + state + queues │
└─────────────┬────────────┘
              │
              v
┌──────────────────────────┐
│ Audio/LLM/tool loop      │
│ STT -> LLM -> TTS        │
└─────────────┬────────────┘
              │
              v
┌──────────────────────────┐
│ Cleanup + Kafka log      │
└──────────────────────────┘
```

Telephony/browser client
-> FastAPI websocket endpoint `/connect_call_airtel`
-> call metadata parsing
-> Redis/mock call configuration
-> prompt + node + model + STT + TTS setup
-> `StreamingConversation`
-> STT / LLM / actions / TTS workers
-> outbound audio and termination events
-> Kafka log at cleanup

## Key entrypoints

`main.py`

- Defines FastAPI app lifecycle.
- Starts the Kafka producer.
- Creates shared HTTP clients for bank APIs.
- Preloads prompt files into in-memory stores.
- Hosts `/connect_call_airtel`, the main websocket endpoint.
- Builds per-call objects: transcriber, synthesizer, `ChatGPTAgent`, action factory, output device, and phone conversation.

`vocode/streaming/streaming_conversation.py`

- Core orchestration engine.
- Owns the active call state, transcript, workers, queues, interruptions, idle checks, duration checks, metrics, and final Kafka logging.
- Wires STT output into agent input, agent output into TTS, and TTS chunks into websocket output.

`vocode/streaming/telephony/conversation/airtel_phone_conversation.py`

- Airtel websocket receive loop.
- Decodes inbound `media.payload` base64 audio.
- Handles `mark`, `stop`, and mock `send-logs` events.

`vocode/streaming/telephony/conversation/nexus_phone_conversation.py`

- Nexus websocket receive loop.
- Accepts binary audio frames.
- Uses Nexus-specific output event format.

## Important directories

`flows/`

Node-based FSM definitions. Each flow declares nodes with:

- `nodeId`
- `nodeName`
- prompt file per language/gender
- initial message per language/gender
- allowed actions/tools
- delay/idle settings
- target node metadata

Examples:

- `plxsell_appt_flow.py`: `authenticate -> plxsell_converse -> plxsell_appointment`
- `collections_flow.py`: `authenticate -> negotiate -> oncall_payment`
- `ntb_flow.py`: `authenticate -> negotiate`

`prompts/`

Prompt text files grouped by usecase. Prompt selection depends on:

- usecase
- current node
- language
- speaker gender
- dynamic metadata
- sometimes optimizer/prompt-management labels

`prompts/prompt_store.py` and `prompts/promptstore_jinja.py`

- Load prompt files once at startup.
- Serve raw prompts or Jinja-rendered prompts from memory.

`prompt_management/`

Optional prompt-manager integration for optimizer/mock workflows. The current production code path keeps `prompt_management_usecases = []`, so legacy file prompts are usually used unless the request is a mock optimizer call.

`vocode/streaming/agent/`

LLM agent implementation. `chat_gpt_agent.py` builds OpenAI/Azure chat parameters from prompt preamble plus transcript and streams model output.

`vocode/streaming/action/`

LLM-callable tool implementations. Tools perform business actions, validate inputs, call APIs, set flags, switch state, or terminate calls.

`vocode/streaming/usecase_handler/`

Usecase-specific hooks for initializing conversation variables, rendering prompts, and doing node-switch work. Currently specialized for `CollectionsPDM`, `CCLI`, and `NTB`; other usecases use the base handler.

`clients/`

Shared clients, especially Kafka producer setup.

`config/`

Static configuration maps for model deployments, voice IDs/settings, bot names, usecase/product prompt variables, payment modes, etc.

## Layered view

```text
┌────────────────────────────────────────────────────────────────────┐
│ API / transport layer                                              │
│ main.py, AirtelPhoneConversation, NexusPhoneConversation, outputs  │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────v─────────────────────────────────────┐
│ Streaming orchestration layer                                      │
│ StreamingConversation, workers, transcript, interruption handling   │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────v─────────────────────────────────────┐
│ ML layer                                                           │
│ Transcribers, ChatGPTAgent, model config, synthesizers             │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────v─────────────────────────────────────┐
│ Business conversation layer                                        │
│ flows, prompts, usecase handlers, actions/tools                    │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────v─────────────────────────────────────┐
│ Data/integration layer                                             │
│ Redis config, Kafka logs, payment/SFDC/OfferMart/CDP APIs          │
└────────────────────────────────────────────────────────────────────┘
```

## Main call object graph

At websocket start, `main.py` creates:

`BaseUserConfig`
-> `NODES`
-> `ChatGPTAgentConfig`
-> `ChatGPTAgent`
-> transcriber instance
-> synthesizer instance
-> output device
-> `AirtelPhoneConversation` or `NexusPhoneConversation`
-> `StreamingConversation.start()`

Inside `StreamingConversation`, workers are connected like this:

Inbound audio
-> transcriber
-> `TranscriptionsWorker`
-> `ChatGPTAgent`
-> `AgentResponsesWorker`
-> synthesizer
-> `SynthesisResultsWorker`
-> output device
-> websocket

When the LLM emits a function/tool call:

`ChatGPTAgent`
-> `ActionsWorker`
-> concrete action
-> action result
-> either back to agent, switch node, or terminate call

Visual object graph:

```text
main.py
  │
  ├─ BaseUserConfig
  │    └─ metadata, usecase, language, model ids, speaker, transcriber/TTS choices
  │
  ├─ flow nodes from flows/<usecase>_flow.py
  │    └─ current node starts as "authenticate"
  │
  ├─ ChatGPTAgentConfig
  │    ├─ prompt_preamble
  │    ├─ initial_message
  │    ├─ actions for current node
  │    └─ primary + fallback model config
  │
  ├─ ChatGPTAgent
  │    └─ action factory for this usecase
  │
  ├─ Transcriber: Deepgram / Azure / Mock
  ├─ Synthesizer: ElevenLabs / Azure / Smallest / Mock
  ├─ OutputDevice: AirtelOutputDevice / NexusOutputDevice
  │
  └─ PhoneConversation
       └─ StreamingConversation.start()
```

Worker wiring inside `StreamingConversation`:

```text
                          ┌───────────────────────┐
                          │ ActionsWorker         │
                          │ tool execution + FSM  │
                          └───────────▲───────────┘
                                      │ function call
                                      │ action result
                                      │
Inbound audio                         │
from websocket                        │
      │                               │
      v                               │
┌─────────────┐   transcript   ┌──────┴──────┐   text/tool   ┌────────────────┐
│ Transcriber │ ─────────────> │ ChatGPTAgent│ ────────────> │ AgentResponses │
└─────────────┘                └─────────────┘               │ Worker         │
      ▲                                                       └───────┬────────┘
      │                                                               │ text
      │                                                               v
      │                                                       ┌────────────────┐
      │                                                       │ Synthesizer    │
      │                                                       └───────┬────────┘
      │                                                               │ audio chunks
      │                                                               v
      │                                                       ┌────────────────┐
      └──────────────── interrupt/barge-in handling ──────── │ OutputDevice   │
                                                              └───────┬────────┘
                                                                      │
                                                                      v
                                                              websocket client
```
