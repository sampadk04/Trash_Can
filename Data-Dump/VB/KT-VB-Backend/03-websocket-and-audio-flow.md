# Websocket And Audio Flow

## Main websocket endpoint

The primary endpoint is:

`/connect_call_airtel`

Despite the name, it supports:

- Airtel-style JSON media events.
- Browser calls using Airtel-style framing but different audio config.
- Nexus calls using an initial metadata string and binary audio frames.

Connection setup:

```text
websocket connect
      │
      v
main.py accepts
      │
      v
read first message
      │
      ├─ JSON {"event": "connected"}
      │     │
      │     v
      │   read second "start" message
      │     │
      │     v
      │   Airtel/browser path
      │
      └─ non-JSON / metadata string
            │
            v
          Nexus path
      │
      v
resolve case_id + stream id
      │
      v
load BaseUserConfig
      │
      v
build STT + LLM + TTS + output device
      │
      v
start provider conversation
```

Client connects
-> FastAPI accepts websocket
-> first message is inspected
-> if JSON `{"event": "connected"}`: Airtel/browser path
-> else: Nexus metadata string path
-> call config is loaded
-> conversation object starts
-> websocket receive loop begins

## Airtel/browser inbound protocol

Expected opening messages:

1. `connected` event JSON.
2. `start` event JSON containing `streamSid`, `callerNumber`, and `customParameters`.

Important `customParameters`:

- `caseId`
- `isMockCall`
- `transcriber`
- `synthesizer`
- optimizer filters for mock prompt tests

Inbound audio:

Airtel sends JSON:

`{"event": "media", "media": {"payload": "<base64-audio>"}}`

Message shape:

```text
Airtel inbound message
┌────────────────────────────────────────────┐
│ event: "media"                             │
│ streamSid: "..."                           │
│ media:                                     │
│   payload: base64(8 kHz MULAW audio bytes) │
└────────────────────────────────────────────┘
```

Flow:

websocket text
-> `AirtelPhoneConversation._handle_ws_message`
-> base64 decode `media.payload`
-> `receive_audio(chunk)`
-> STT transcriber

Other events:

- `mark`: output-device playback acknowledgement; passed to `AirtelOutputDevice`.
- `stop`: breaks receive loop and triggers cleanup.
- `send-logs`: mock/testing path that sends logs back on websocket.

Outbound audio:

Synthesized bytes
-> `AirtelOutputDevice.play`
-> base64 encode
-> send JSON:

`{"event": "media", "streamSid": "...", "media": {"payload": "<base64-audio>"}}`

```text
TTS audio bytes
      │
      v
AirtelOutputDevice.play()
      │
      v
base64 encode
      │
      v
websocket.send_text({
  event: "media",
  streamSid: conversation_id,
  media: { payload: "..." }
})
```

Termination:

`StreamingConversation.call_termination_message`
-> JSON:

`{"event": "terminate", "streamSid": "...", "reason": {"code": "1|2", "text": "..."}}`

Code `2` is used for live transfer/handoff scenarios in several usecases. Code `1` is normal hangup.

## Nexus inbound protocol

Nexus first message is a semicolon-delimited metadata string, for example:

`case_id=...;interaction_id=...;browser=False`

Flow:

metadata text
-> parse into dict
-> `case_id` is required
-> `interaction_id` becomes conversation id when present
-> Nexus audio config is selected
-> `NexusPhoneConversation` starts

Inbound audio:

websocket binary frame
-> `NexusPhoneConversation.attach_ws_and_start`
-> `message.get("bytes")`
-> `receive_audio(chunk)`
-> STT transcriber

```text
Nexus inbound
┌──────────────────────────┐
│ first frame: metadata    │
│ later frames: raw bytes  │
└────────────┬─────────────┘
             │
             v
NexusPhoneConversation.receive loop
             │
             v
StreamingConversation.receive_audio()
```

Outbound audio:

Synthesized bytes
-> `NexusOutputDevice.play`
-> base64 encode
-> send JSON:

`{"type": "streamAudio", "data": {"audioDataType": "raw", "sampleRate": 24000, "audioData": "<base64-audio>"}}`

Termination/handoff:

For Nexus, termination data uses an action shape:

Normal hangup:

`{"data": {"action": "hangup", "metadata": {"interaction_id": "..."}}}`

Agent handoff:

`{"data": {"action": "agent_handoff", "metadata": {"sg": "Turbo_Jarvis_Cisco", "an": "<ucic>"}}}`

## Audio worker flow

Inbound path:

```text
INBOUND AUDIO

websocket frame
  -> AirtelPhoneConversation / NexusPhoneConversation
  -> StreamingConversation.receive_audio()
  -> StreamingConversation.consume_nonblocking()
  -> optional BaseDenoiser
  -> DeepgramTranscriber / AzureTranscriber / MockTranscriber
  -> TranscriptionsWorker.process()
  -> ChatGPTAgent input queue
```

websocket
-> provider conversation
-> `StreamingConversation.consume_nonblocking`
-> optional denoiser
-> transcriber
-> `TranscriptionsWorker`
-> LLM agent

Outbound path:

```text
OUTBOUND AUDIO

ChatGPTAgent generated text
  -> AgentResponsesWorker
  -> synthesizer.create_speech()
  -> SynthesisResult.chunk_generator
  -> SynthesisResultsWorker
  -> send_speech_to_output()
  -> OutputDevice.consume_nonblocking(AudioChunk)
  -> AirtelOutputDevice.play() / NexusOutputDevice.play()
  -> websocket text message
```

LLM text
-> `AgentResponsesWorker`
-> TTS `create_speech`
-> `SynthesisResult.chunk_generator`
-> `SynthesisResultsWorker`
-> `send_speech_to_output`
-> output device queue
-> websocket

## Interruptions

Jarvis supports barge-in:

```text
Bot is speaking
      │
      v
Customer interrupts
      │
      v
STT produces meaningful partial/final transcript
      │
      v
TranscriptionsWorker detects human speech
      │
      v
broadcast_interrupt()
      │
      ├─ interrupts queued audio chunks
      ├─ output_device.interrupt()
      ├─ cancels current agent response task
      ├─ cancels action worker task when applicable
      └─ marks bot transcript as partial if cut off
      │
      v
Final user transcript goes to LLM
```

User starts speaking while bot audio is playing
-> `TranscriptionsWorker` detects meaningful speech
-> `broadcast_interrupt`
-> interrupts queued audio events
-> cancels current agent/TTS/action worker tasks
-> output device interrupt stops playback
-> transcript marks partial bot message
-> latest user final transcript goes to LLM

Short acknowledgements/backchannels can be ignored while bot is speaking, depending on interrupt sensitivity and word count.

## Initial message and readiness

At `StreamingConversation.start()`:

```text
start()
  │
  ├─ transcriber.start()
  ├─ transcriptions_worker.start()
  ├─ agent_responses_worker.start()
  ├─ synthesis_results_worker.start()
  ├─ output_device.start()
  ├─ optional denoiser.start()
  ├─ usecase startup tasks
  │    ├─ payment link task for collections
  │    ├─ OfferMart/Paperless/CDP tasks for PLX
  │    └─ offer fetch task for CCBalCon
  ├─ wait for transcriber.ready()
  ├─ agent.start()
  ├─ send initial message
  ├─ start idle monitor
  └─ start max-duration monitor
```

transcriber starts
-> workers start
-> synthesizer/output device start
-> usecase startup tasks may start
-> agent starts
-> initial node message is synthesized and sent
-> `initial_message_tracker` is set
-> user speech starts being processed after the initial message is complete

## Idle and duration monitors

Two background tasks run during live calls:

Idle monitor:

```text
last_action_timestamp too old
      │
      v
send "are you there?" nudge
      │
      v
customer responds?
      │
      ├─ yes -> reset counter
      │
      └─ no  -> repeat until threshold
                  │
                  v
                send closure message
                  │
                  v
                terminate call
```

No activity past node/usecase idle threshold
-> ask if human is present
-> repeat up to configured count
-> send not-responsive closing message
-> provider termination event

Duration monitor:

```text
call duration >= usecase max
      │
      v
interrupt current output
      │
      v
detect ongoing language
      │
      v
send duration-exceeded message
      │
      v
choose normal termination or live-transfer code
      │
      v
send provider termination event
```

Call duration exceeds usecase max
-> interrupt current bot output
-> send max-duration closure/live-transfer message
-> wait briefly
-> terminate or handoff depending on usecase
