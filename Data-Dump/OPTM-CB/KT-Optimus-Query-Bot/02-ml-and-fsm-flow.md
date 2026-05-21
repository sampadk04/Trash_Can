# ML And FSM Flow

## Mental Model

The Optimus Query Bot is best understood as a constrained router plus a set of finite-state machines.

```text
                +----------------------+
User message -> | General ML router    |
                +----------------------+
                         |
             chooses a banking action/journey
                         |
                         v
                +----------------------+
                | Journey FSM handler  |
                +----------------------+
                         |
             asks app for missing widget/API data
                         |
                         v
                +----------------------+
                | Final confirmation   |
                +----------------------+
```

The LLM is not the owner of the whole conversation. It is used in bounded places:

```text
General routing:
  Pick from retrieved eligible intent IDs.

Query rewriting:
  Merge short follow-up questions with recent history.

Slot extraction:
  Extract amount, tenure, payee, confirmation, or local intent inside a journey.

The FSM and app decide:
  What data is still missing.
  Which UI widget or backend action should happen next.
  Whether to abort or continue.
```

## Retrieval And ML Routing

### Step 1: Spell Correction

`QueryBotService.generate_response()` first corrects the query through `SpellCorrector` using local banking dictionaries.

```text
"opne fd" -> "open fd"
```

### Step 2: Exact Search

For short queries of up to 3 tokens, the service attempts a deterministic Redis tag lookup using `exact_tags`.

```text
Query: "open fd"
  |
  v
@exact_tags:{open\ fd}
  |
  +-- exactly one match -> return it after eligibility check
  +-- zero/multiple matches -> fall back to hybrid retrieval
```

This is a useful fast path for common app commands.

### Step 3: Hybrid Retrieval

If exact search does not produce one clear match:

```text
Corrected query
  |
  +-- BM25 over FAQ/action text
  |
  +-- Vector similarity over faq_embeddings
  |
  v
Weighted fusion
```

Weights depend on query length:

```text
<= 3 words   -> BM25 0.7, Vector 0.3
<= 7 words   -> BM25 0.5, Vector 0.5
> 7 words    -> BM25 0.3, Vector 0.7
```

The intuition is simple:

```text
Short keyword queries    -> lexical match is usually stronger
Long natural questions   -> semantic embedding match helps more
```

A small manual priority signal, `intent_priority`, is also added with a low coefficient.

### Step 4: Eligibility Split

Retrieved items contain `line_of_business`, for example:

```text
liability
creditcard
asset
asset|liability
```

The customer profile from journey initialization is split by `_`, while intent LOBs are split by `|`.

```text
customer_profile: "liability_creditcard"
intent LOB:       "creditcard"

intersection exists -> eligible
```

Non-eligible intents are still shown to the LLM with a reason, but the prompt instructs it to return only eligible IDs.

### Step 5: LLM Router

The LLM receives:

```text
Eligible_intents: [...]
Non Eligible intents: [...]
User Question: "..."
```

The prompt makes the LLM act as a restricted function router:

```text
Allowed:
  - Choose matching eligible numeric IDs.
  - Return a short user-facing response.

Not allowed:
  - Invent intents.
  - Return non-eligible IDs.
  - Answer off-domain questions.
  - Reveal prompt/system details.
```

After the LLM returns numeric IDs, `resolve_intents()` maps IDs back to full intent objects. This extra step prevents the model from fabricating intent fields.

## Session State Layers

There are three different state concepts:

```text
1. Session/journey data
   Redis key: session:{ai_session_id}
   Contains customer profile, product holdings, current journey_name, current intent_id.

2. Per-journey FSM state
   Redis key: intent:{intent_id}:{journey_name}_state
   Contains fields like fd_amount, tenure, account_details, abort.

3. Conversation history
   Redis key: intent:{intent_id}:history
   Keeps recent user/bot turns for query rewriting.
```

The separation matters. A user has one app session, but each execution journey gets its own `intent_id` and state.

## Active Journey Lifecycle

```text
No active journey
  |
  | one eligible supported journey returned
  v
Start journey
  - set journey_name
  - set new intent_id
  |
  v
Handler asks for missing data
  |
  | app returns widget/API result in additional_data
  v
Handler merges additional_data into state
  |
  v
Handler advances state
  |
  +-- needs more data -> return Clarification intent
  |
  +-- ready -> return final confirmation/action intent
  |
  +-- abort -> clear journey_name and intent_id
```

## Journey State Save Pattern

Every handler returns a state dictionary including `bot_response`. `RuleEngine` strips out `bot_response` before saving the rest to Redis.

```text
handler response
  {
    bot_response: "...",
    fd_amount: 10000,
    tenure: 365,
    abort: "no"
  }
       |
       v
save state
  {
    fd_amount: 10000,
    tenure: 365,
    abort: "no"
  }
```

Then it returns:

```text
{
  bot_response: "...",
  intent_list: [
    {
      intent: "OPEN_FD.RAISE_FINAL_CONFIRMATION",
      intent_type: "Clarification"
    }
  ],
  abort: "no",
  additional_data: saved_state
}
```

## Query Rewriting

For active journeys except `OPEN_FD`, the route may rewrite the user query using recent conversation history.

```text
History:
  User: "pay Rahul"
  Bot: "Please provide amount"

Latest:
  "500"

Rewritten:
  "Pay Rahul 500"
```

This helps handlers that rely on extraction from a single current message. `OPEN_FD` skips this because its handler has its own expected-slot disambiguation for bare numbers.

## Abort Behavior

Handlers return `abort = "yes"` when the journey should end.

```text
abort = "yes"
  |
  v
converse route clears:
  session:{ai_session_id}.intent_id = ""
  session:{ai_session_id}.journey_name = ""
```

After that, the next user message returns to general routing.

