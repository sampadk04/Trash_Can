# Core ML And FSM Flow

## The ML pipeline

The main voice loop is:

```text
Customer speaks
      │
      v
Audio bytes over websocket
      │
      v
Provider conversation class
      │
      v
StreamingConversation.receive_audio()
      │
      v
Deepgram/Azure/Mock STT
      │
      v
Final transcript
      │
      v
TranscriptionsWorker
      │
      ├─ filters noise/backchannels
      ├─ handles barge-in
      ├─ updates conversation context
      └─ sends final user turn to agent
      │
      v
ChatGPTAgent
      │
      ├─ prompt preamble
      ├─ transcript
      ├─ current node tools
      └─ Azure/OpenAI model
      │
      v
LLM output
      │
      ├─ normal text ────────────────┐
      │                              v
      └─ function/tool call -> ActionsWorker
                         │           │
                         │           v
                         │    node switch / API / terminate
                         │
                         v
AgentResponsesWorker
      │
      v
TTS synthesizer
      │
      v
Audio chunks to output device
      │
      v
Customer hears bot
```

Customer speech
-> websocket audio frame
-> provider conversation receives bytes
-> `StreamingConversation.receive_audio`
-> optional denoiser
-> STT transcriber
-> final transcript
-> `TranscriptionsWorker`
-> `ChatGPTAgent`
-> Azure/OpenAI streaming chat completion
-> text chunks or function calls
-> `AgentResponsesWorker`
-> TTS synthesizer
-> audio chunks
-> output device websocket send
-> customer hears bot

## STT layer

Configured in `main.py` from `user_call_config.transcriber` or request overrides.

Supported choices in the main path:

- `Deepgram`: default live STT path. Uses `DeepgramTranscriberConfig`, in-house API key, Hindi language, and model from `user_call_config.transcriber_model` or `nova-2`.
- `Azure`: Azure speech recognizer path.
- `Mock`: testing path.

Input audio config depends on the source:

- Airtel telephony: 8 kHz MULAW, chunk size 160.
- Browser: 44.1 kHz LINEAR16 input, 24 kHz LINEAR16 output.
- Nexus: 8 kHz LINEAR16 input, 24 kHz LINEAR16 output.

`TranscriptionsWorker` filters and shapes STT output before LLM:

- ignores empty/backchannel-like snippets
- handles repeated final transcripts
- interrupts current bot audio when the user speaks
- blocks transcription during critical transition/tool moments
- can delay processing for nodes that need a longer speech wait window
- records STT latency
- appends user turns to `global_conversation_context`

## LLM layer

The active LLM agent is usually `ChatGPTAgent`.

Model selection:

`BaseUserConfig.llm_model_id`
-> lookup in `config/llm_model_config.py` by `ENV`
-> `AzureOpenAIConfig`
-> primary OpenAI/Azure client

Fallback:

`BaseUserConfig.fallback_model_id`
-> secondary `AzureOpenAIConfig`
-> `LLMFallback`
-> used when primary stream creation fails

Finetuned path:

- If `metadata.use_finetuned_model == "true"` and usecase is `PLXsellAppointment`, `main.py` routes to `PLXsellAppointmentFinetuned`.
- Finetuned model configs contain `deployment_name` and `actual_azure_endpoint`.
- `ChatGPTAgent` uses a flat API gateway transport and a finetuned EntAuth/Kong token when configured.

LLM request construction:

Prompt preamble
-> current transcript
-> function definitions for current node actions
-> model, temperature, max tokens
-> streamed chat completion

The prompt preamble comes from the active node's prompt file after variable interpolation.

LLM request mental model:

```text
System prompt for active node
  + dynamic metadata values
  + prior transcript for current node
  + optional conversation_so_far from previous node
  + OpenAI function schemas for current node actions
  + model settings from BaseUserConfig
  =
Chat completion request
```

## Prompt lifecycle

Startup:

`main.py` lifespan
-> preload `PROMPTS_DIR` into `prompt_store`
-> preload same tree into `prompt_store_jinja`

```text
prompts/
  ├─ PLXSell/*.txt
  ├─ TS1ReleaseCollections/*.txt
  ├─ NTB/*.txt
  └─ ...
        │
        v
startup preload
        │
        ├─ prompt_store: raw file text
        └─ prompt_store_jinja: Jinja-capable templates
```

Call start:

`main.py`
-> determine usecase
-> load `NODES`
-> choose initial node `nodeId == 1`
-> read/render node prompt
-> fill `{variables}` from `user_call_config.metadata`
-> fill initial bot greeting variables
-> create `ChatGPTAgentConfig(prompt_preamble=prompt, initial_message=...)`

```text
usecase + language + speaker_gender
      │
      v
flow node
      │
      ├─ systemPromptFile[language][speaker_gender]
      └─ initialMessage[language][speaker_gender]
      │
      v
prompt template
      │
      ├─ Jinja render when needed
      └─ Python .format(**metadata)
      │
      v
active prompt_preamble + initial bot message
```

Node switch:

Tool returns `next_stage`
-> `ActionsWorker.switch_to_stage`
-> finds target node by `nodeName`
-> optionally sends a transition/filler message
-> runs usecase-specific node switch processing
-> reads/renders new prompt
-> interpolates metadata and optional `conversation_so_far`
-> replaces `agent.agent_config.prompt_preamble`
-> replaces `agent.agent_config.actions`
-> rebuilds OpenAI function definitions
-> resets transcript for the new node

## FSM model

There is no separate FSM library. The FSM is a node list plus action outputs.

Generic FSM loop:

```text
┌────────────────────────────────────────────────────┐
│ Current node                                       │
│ - active prompt                                    │
│ - active tools                                     │
│ - node-specific delay/idle settings                │
└──────────────────────┬─────────────────────────────┘
                       │ user says something
                       v
┌────────────────────────────────────────────────────┐
│ LLM responds                                       │
│ - plain text, or                                   │
│ - function/tool call                               │
└──────────────────────┬─────────────────────────────┘
                       │
                       v
┌────────────────────────────────────────────────────┐
│ Action result                                      │
│ - normal response                                  │
│ - next_stage                                       │
│ - end_call                                         │
└──────────────┬───────────────┬─────────────────────┘
               │               │
               │               └───────────────┐
               v                               v
     back to same node               terminate / handoff
               │
               v
       switch_to_stage()
               │
               v
      new prompt + new tools
```

Node definition contains:

- `nodeName`: current state name.
- `systemPromptFile`: prompt file path by language and gender.
- `initialMessage`: optional first bot utterance for that node.
- `actions`: tools the LLM may call in that node.
- `onEndTransferToNode`: descriptive next node id used by the flow design.
- `requiresSessionConversation`: whether to inject previous node conversation into the next prompt.
- delay/idle settings such as `enable_delayed_processing` and `idle_time_threshold`.

State transition shape:

Current node prompt
-> LLM response or tool call
-> tool action executes
-> action returns one of:
   - no transition: result is passed back to LLM
   - `next_stage`: switch active node
   - `end_call`: send provider termination event

Examples:

PLX appointment:

```text
authenticate
  │
  │ action_customer_authenticated
  v
plxsell_converse
  │
  │ action_customer_convinced
  v
plxsell_appointment
  │
  ├─ action_capture_appointment_datetime
  ├─ action_capture_negative_profile
  ├─ action_confirm_location_preference
  └─ action_terminate_call
        │
        v
normal hangup / live transfer / fallback appointment cleanup
```

`authenticate`
-> customer confirms identity
-> `action_customer_authenticated`
-> `plxsell_converse`
-> customer is convinced
-> `action_customer_convinced`
-> `plxsell_appointment`
-> appointment/location tools
-> terminate or live transfer

Collections:

```text
authenticate
  │
  │ action_customer_authenticated
  v
negotiate
  │
  ├─ action_validate_ptpdate
  ├─ action_send_payment_link
  ├─ action_send_deep_payment_link
  ├─ action_set_emi_offer
  ├─ action_guideoncall_payment
  │       │
  │       v
  │   oncall_payment
  │       │
  │       ├─ action_check_payment_status
  │       └─ action_terminate_call
  │
  └─ action_terminate_call
```

`authenticate`
-> customer confirms identity
-> `negotiate`
-> promise/payment/link/offer tools
-> optional `oncall_payment`
-> payment validation or termination/live transfer

NTB:

```text
authenticate
  │
  │ action_customer_authenticated
  v
negotiate
  │
  ├─ action_recommend_card
  ├─ action_get_card_benefits
  ├─ action_find_better_benefit
  ├─ action_get_unsecured_rebuttal
  ├─ action_send_diy_link
  └─ action_terminate_call
```

`authenticate`
-> customer confirms identity
-> `negotiate`
-> recommend-card / benefits / rebuttal / DIY-link tools
-> terminate

## Tools/actions

Actions are exposed to the LLM as OpenAI function definitions. The current node controls which actions are available.

Important action categories:

- Authentication: confirms right customer and moves out of `authenticate`.
- Termination: sends provider-level hangup or handoff event.
- Payment: send link, deep link, UPI collect, validate OCOP/payment.
- Sales: calculate EMI, create leads, capture appointment date/time, capture address/location, detect negative profile.
- CCLI/CCBalCon/NTB: offer fetch/update, security checks, card recommendation, benefit lookup.
- Live transfer: mark/trigger handoff flows.

Tool result semantics:

```text
LLM function_call(name, arguments)
      │
      v
ChatGPTAgent.call_function()
      │
      v
ActionsWorker.process()
      │
      v
Concrete action.run()
      │
      v
ActionOutput.response
      │
      ├─ no flags
      │    └─ ActionResultAgentInput -> LLM continues in same node
      │
      ├─ next_stage = "some_node"
      │    └─ switch_to_stage() -> replace prompt/actions/transcript
      │
      └─ end_call = true
           └─ call_termination_message() -> provider terminate/handoff event
```

Action output
-> if normal result: action output becomes an agent input and the LLM may continue
-> if `next_stage`: FSM switch happens and prompt/actions are replaced
-> if `end_call`: termination message is sent to the provider

## Conversation state

`StreamingConversation` carries both generic and usecase-specific state:

- `current_node`
- `global_conversation_context`
- transcript and worker queues
- latency metrics
- termination flags and live-transfer flags
- API status flags
- usecase-specific counters and captured fields

The final Kafka payload is built mostly from this state plus `BaseUserConfig.metadata`.

State ownership visual:

```text
BaseUserConfig.metadata
  ├─ mostly input/customer/business fields
  ├─ prompt variables
  └─ final log fields

StreamingConversation
  ├─ live state: current_node, transcript, timers
  ├─ derived state: latency, language, current prompt stage
  ├─ business flags: live transfer, appointment complete, payment done
  └─ API status fields: offermart, paperless, SFDC, CCBalCon, CCLI, etc.

Actions/usecase helpers
  ├─ mutate StreamingConversation fields
  ├─ mutate metadata when prompt/log fields change
  └─ call external APIs
```
