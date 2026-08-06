Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.


---

Here is my brief one page handoff executive summary of the Optimus V2 Chatbot (like the philosophy and the objective and the architecture on a very high level, i.e. the important bits like the parallel blocks, the precedence, the hybrid retrieval of intents etc.)
"""
# Optimus V2 Chatbot — Executive Handoff Summary

## Purpose and philosophy

Optimus V2 is the banking-conversation orchestration layer for NEXUS ML. Its objective is to convert a customer message into the correct conversational response, banking journey, or frontend action—safely, quickly, and without breaking published API contracts.

The design is deliberately scenario-first and maintainer-friendly: the flow of one customer turn should be understandable in one screen. Each block has clear ownership, speculative work cannot mutate state, customer data is masked before orchestration, and every successful request is persisted exactly once.

V2 modernizes orchestration while retaining proven V1 FSM handlers for supported guided journeys.

## High-level architecture

```text
Masked request
    ↓
Orchestrator selects one scenario
    ↓
Guardrail / ChitChat / Rephraser / MID / IFB or FSM
    ↓
Intent Coordinator routes the accepted decision
    ↓
Single finalizer validates, persists, and returns the public response
```

The five logical capability areas are:

- **Guardrail:** Deterministic policy checks plus contextual LLM-based safety evaluation where applicable.
- **ChitChat:** Separates greetings, small talk, and basic questions from banking-intent traffic.
- **Rephraser:** Contextually rewrites only queries that cannot be retrieved reliably in isolation.
- **MID:** Retrieves, filters, disambiguates, and locks the banking intent.
- **IFB/FSM:** IFB handles intent-specific conversational fulfilment; FSM runs supported deterministic guided journeys.

## Turn precedence

Every request follows a strict precedence:

1. **Exact previous-response pill selection**  
   A `skip_llm=true` selection is validated against the option ledger from the immediately previous response and dispatched directly.

2. **Deterministic Guardrail**  
   Runs synchronously before any normal scenario. A failure stops the turn immediately.

3. **Active FSM continuation**  
   If a guided FSM journey owns the conversation, it continues first.

4. **Active IFB continuation**  
   If an intent-fulfilment conversation is active, it retains ownership unless it detects abandonment or an intent switch.

5. **General-query orchestration**  
   Used when no IFB or FSM journey is active.

This ordering prevents a new retrieval result from accidentally stealing ownership from an active banking journey.

## Parallel-block strategy

For a general query, V2 starts several write-free operations concurrently:

- non-deterministic Guardrail;
- ChitChat classification;
- optional contextual Rephraser;
- speculative hybrid retrieval and MID processing.

Completion time does not determine authority—the await order enforces business precedence:

```text
Guardrail → ChitChat → Rephraser decision → MID
```

A Guardrail failure discards all lower-priority work. A non-banking ChitChat result discards Rephraser and MID. If no rewrite is needed, the speculative MID result is reused; otherwise, it is discarded and MID reruns using the rewritten query.

Active IFB turns have their own internal parallelism: a small switch-detection call races the main fulfilment call. The main call performs entity extraction, completion, response generation, and an embedded safety check. If abandonment wins, the main result is discarded and MID receives contextual handoff information. Active FSM turns rely on the deterministic pre-check and the reused deterministic FSM handler.

## Hybrid intent retrieval and routing

MID uses Reciprocal Rank Fusion over three independent, concurrently executed searches:

- intent-vector similarity;
- example-query vector similarity;
- intent-only BM25 keyword search.

The base result is the RRF-ranked top 15 intents. High-similarity example matches enrich existing candidates or append a missing parent intent. Only examples matched on the current turn are supplied to MID as evidence.

In the semantic path, the preprocessed customer query and each intent's canonical `title + description` are represented as dense embedding vectors. A cosine-similarity KNN search retrieves intents that are conceptually related even when the customer's vocabulary does not exactly match the configured wording. This complements BM25, which remains valuable for exact banking terms, product names, acronyms, and other lexical signals. The two independently ranked result sets are combined through RRF so that neither semantic nor keyword matching alone controls the candidate set.

Curated hard example queries are embedded as separate documents and searched concurrently with the canonical intent vectors. Keeping them separate is important: it lets a very close customer-query-to-example match recover or strengthen the owning intent without expanding its description or distorting its normal semantic and BM25 representation. Only high-confidence examples matched for the current turn are fused into the candidate list; the complete stored example catalogue is never passed to MID.

Semantic embedding quality is a critical dependency because MID can only disambiguate among the candidates retrieval supplies. Some colloquial, indirect, product-specific, or otherwise difficult customer queries do not semantically align strongly enough with the intended intent's title and description. When that target intent is absent from the top-15 itself, MID cannot select it regardless of the quality of its downstream reasoning. The example-query enhancement improves recall for curated hard cases, but it is a tactical safeguard rather than a complete solution to weak semantic matching.

The strategic direction should therefore include evaluating stronger embedding models and potentially fine-tuning one on labelled intent-level customer queries. Training with representative paraphrases and hard negatives from easily confused intents would improve top-k intent recall, similarity calibration, and disambiguation before MID. Model selection should be driven by an offline retrieval benchmark—especially Recall@15 on difficult and ambiguous queries—because improving candidate recall reduces both MID errors and the need to continually add handcrafted examples.

Before locking an intent, MID applies eligibility and production-catalogue filters, supported-FSM filtering, same-turn exclusions, direct-intent continuity, and deterministic locking of a uniquely named recent option. The LLM is used only after those deterministic stages.

An accepted intent can resolve to:

- a direct frontend action;
- an IFB conversational fulfilment flow;
- one of the supported FSM journeys;
- an ambiguity response containing intent or entity pills.

If IFB detects a switch, it releases the old intent and invokes MID again in the same turn with handoff context, excluding the released intent to avoid loops.

## State, safety, and contract guarantees

Each successful request creates one unified conversation turn containing only the final accepted block outputs. A single finalizer validates action/option-ledger parity, appends the turn to Redis exactly once, and constructs the response.

Key invariants are:

- speculative work is side-effect-free;
- pills are authorized only by the immediately previous successful response;
- frontend actions cannot fire twice;
- internal candidates, prompts, traces, tokens, and timings never enter the public response;
- Guardrail-only turns do not steal active IFB/FSM ownership;
- customer-data privacy and the existing `/converse` contract remain non-negotiable.

In short, Optimus V2 is an explicit, precedence-driven orchestration engine: parallel where latency benefits, sequential where business authority matters, hybrid in retrieval, conservative in state mutation, and intentionally compatible with established banking journeys.
"""

