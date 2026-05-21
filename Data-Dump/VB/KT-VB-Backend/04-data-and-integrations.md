# Data And Integrations

## Data sources at call start

The runtime call config is a `BaseUserConfig`.

Primary production path:

```text
caseId from websocket/custom params
      │
      v
normalize key: first "_" -> ":"
      │
      v
Redis GET
      │
      v
zstd compressed bytes
      │
      v
decompress to JSON
      │
      v
BaseUserConfig
      │
      ├─ controls usecase and model/STT/TTS selection
      ├─ supplies prompt variables
      └─ supplies post-call log fields
```

`case_id`
-> replace first `_` with `:`
-> Redis key
-> zstd-decompress bytes
-> parse JSON into `BaseUserConfig`

Mock path:

Known mock case ids
-> `mock.get_mock_input(case_id)`
-> parse into `BaseUserConfig`

`BaseUserConfig` includes:

- `caseId`
- `primary_phone_number`
- `usecase`
- `primary_language`
- `synthesizer`
- `transcriber`
- `llm_model_id`
- `fallback_model_id`
- `speaker`
- `speaker_gender`
- `campaign_code`
- `bot_name`
- `transcriber_model`
- `speech_wait`
- `metadata`
- `interaction_intelligence`

Most prompt variables and final log fields come from `metadata`.

## Redis

Redis is used for call configuration lookup.

Relevant files:

- `vocode/streaming/telephony/config_manager/redis_config_manager.py`
- `vocode/streaming/utils/redis.py`

Config:

- `VB_REDIS_HOST`
- `VB_REDIS_PORT`
- `VB_REDIS_PASSWORD`
- SSL enabled with certificate verification disabled.

Read flow:

websocket `caseId`
-> Redis key normalization
-> `RedisConfigManager.get_config`
-> `redis.get`
-> zstd decompress
-> `BaseUserConfig.parse_raw`

The class also has `save_config` and `delete_config`, but the main `/connect_call_airtel` path primarily reads config.

## Kafka

Kafka is used for final conversation/event logging.

Relevant files:

- `clients/kafka/producer.py`
- `vocode/streaming/streaming_conversation.py`

Startup:

FastAPI lifespan
-> `get_producer().start_producing()`
-> `AIOKafkaProducer`
-> SASL_SSL / SCRAM-SHA-512

Config:

- `KAFKA_BROKERS`
- `KAFKA_USERNAME`
- `KAFKA_PASSWORD`
- `KAFKA_TOPIC`

Post-call log flow:

```text
provider receive loop exits
      │
      v
handle_common_conversation_cleanup()
      │
      ├─ PLX appointment fallback / lead creation
      ├─ SFDC live transfer hooks
      ├─ UPI payment link on termination
      ├─ CCBalCon end-of-call API chain
      └─ log_conversation_to_kafka()
              │
              v
       build usecase-specific log_data
              │
              v
       json.dumps(log_data).encode("utf-8")
              │
              v
       Kafka topic from KAFKA_TOPIC
```

websocket closes or call terminates
-> provider conversation cleanup
-> `handle_common_conversation_cleanup`
-> usecase-specific fallback/side effects
-> `conversation.log_conversation_to_kafka`
-> build `log_data`
-> fire-and-forget `producer.send_message(KAFKA_TOPIC, json_bytes)`

Common log fields:

- `conversationId`
- `caseId`
- `usecaseFields`
- `cycle`
- `campaignCode`
- `conversation`
- `usecase`
- `startTime`
- `callDuration`
- `eventTime`
- `endReason`
- `lastState`
- `latency`

`usecaseFields` is heavily usecase-specific. It includes customer/account fields, model IDs, speaker, API statuses, live-transfer fields, captured values, and business counters.

## Prompt storage and prompt management

File prompt path:

```text
Flow node
  │
  ├─ systemPromptFile
  │     └─ prompts/<Usecase>/<prompt>.txt
  │
  ├─ render mode
  │     ├─ prompt_store.get()
  │     └─ prompt_store_jinja.render()
  │
  ├─ variable source
  │     └─ BaseUserConfig.metadata
  │
  v
ChatGPTAgentConfig.prompt_preamble
```

prompt files in `prompts/`
-> loaded into `prompt_store` and `prompt_store_jinja`
-> selected by active flow node
-> rendered with Jinja when needed
-> formatted with metadata variables
-> assigned to `ChatGPTAgentConfig.prompt_preamble`

Prompt manager path:

`PromptManager`
-> `prompt_management/prompts.yaml`
-> resolve label by usecase/workflow/node/filter
-> call external prompt manager API

Current main code has `prompt_management_usecases = []`, so production generally uses file prompts. Mock optimizer calls can still fetch published or temporary prompts by workflow label.

## Shared HTTP clients

`main.py` creates shared `httpx.AsyncClient` instances at startup and stores them in `clients/http/shared.py`.

Examples:

- EntAuth token client.
- Finetuned model EntAuth client.
- OCOP/payment validation client.
- Handoff/client lead APIs.
- Payment link and deep link clients.
- OfferMart.
- SFDC inbound and settlement/collections summary clients.
- CCBalCon entity-lite, EMI simulate, balance conversion clients.
- CCLI entity prime, OfferMart, Commshub clients.
- CDP client.

These clients are reused by action/helper code to avoid recreating HTTP pools per tool call.

Shared-client visual:

```text
FastAPI lifespan startup
      │
      v
clients/http/shared.py globals
      │
      ├─ entauth_client
      ├─ ocop_client
      ├─ handoff_client
      ├─ sendlink_client
      ├─ senddeeplink_client
      ├─ offermart_client
      ├─ sfdc_* clients
      ├─ CCBalCon clients
      ├─ CCLI clients
      └─ cdp_client
      │
      v
actions/helpers reuse these clients during calls
```

## External API touchpoints by usecase

PLX sell / appointment:

- OfferMart fetch at call start.
- Paperless/CDP fetch depending on `new_api`.
- Create lead / create paperless / set appointment / update paperless.
- Live transfer or upper-funnel live transfer decisions.
- Fallback appointment setup during cleanup if appointment tool was used but set appointment did not complete.

Collections:

- Initial payment link can be sent at call start.
- Payment/deep-link tools.
- OCOP/payment validation.
- UPI collect request and payment-link send for UPI collect usecase.
- SFDC live transfer on cleanup when live-transfer intent is set.

Collections charges / mature:

- Payment/deep-link/LCP link tools.
- Partial offer and payment validation.
- SFDC live transfer when configured.

Settlement:

- Dynamic nudging and settlement/foreclosure/partial-payment tools.
- Green-channel/closure/partial payment link tools.
- Settlement live transfer to SFDC when intent is captured.

CCBalCon:

- Offer fetch at call start.
- Entity-lite, EMI simulate, balance conversion, and offer suppression APIs.
- End-of-call API chain in cleanup.

CCLI:

- Entity Prime inquiry/update.
- OfferMart new limit fetch.
- Commshub/Cogno link actions.
- Security check actions.

NTB:

- Uses local card catalog JSON files for recommendation/benefit reasoning.
- DIY link tool can trigger customer journey link.

Usecase integration map:

```text
PLX / PLX Appointment
  -> OfferMart
  -> Paperless / CDP
  -> create lead / create loan / appointment APIs
  -> handoff/live transfer

Collections / UPI Collect / Charges
  -> payment link / deep link
  -> OCOP payment validation
  -> UPI collect request
  -> SFDC live transfer

Settlement
  -> settlement summary / payment links
  -> dynamic nudging helpers
  -> SFDC settlement live transfer

CCBalCon
  -> entity-lite
  -> EMI simulate
  -> balance conversion
  -> OfferMart suppression

CCLI
  -> Entity Prime
  -> OfferMart
  -> Commshub / Cogno

NTB
  -> local card catalog JSON
  -> DIY-link action
```

## Conversation cleanup

Cleanup is centralized in `handle_common_conversation_cleanup`.

```text
normal stop / websocket disconnect / termination event
      │
      v
provider finally block
      │
      v
handle_common_conversation_cleanup()
      │
      ├─ usecase final side effects
      ├─ Kafka log
      ├─ websocket close
      └─ conversation.terminate()
              │
              ├─ cancel monitor/background tasks
              ├─ tear down TTS, agent, STT, workers
              ├─ flush events manager
              └─ clear large in-memory structures
```

Provider receive loop exits
-> run usecase-specific finalization
-> maybe set PLX appointment fallback
-> maybe create PLX lead
-> maybe trigger SFDC live transfer
-> maybe send UPI payment link
-> maybe run CCBalCon end-of-call API chain
-> log conversation to Kafka once
-> close websocket
-> terminate conversation workers/resources

This means many important side effects happen after websocket disconnect, not only during LLM tool calls.

## Mental model for database/storage interactions

Jarvis itself is not doing heavy direct relational database work in the core path. The core backend mostly:

- reads call configuration from Redis,
- writes final structured call logs to Kafka,
- calls downstream bank services that own their own systems of record,
- keeps in-call state in memory on the `StreamingConversation` object.
