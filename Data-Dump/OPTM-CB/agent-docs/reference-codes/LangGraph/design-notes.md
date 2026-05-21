# Designing Systems with LangGraph


## Start with the Process

Before writing graph code, describe the real workflow:

1. What enters the system?
2. What decisions are needed?
3. What external data/actions are needed?
4. What output should be returned?
5. Where can the system stop, retry, or ask for review?

Turn each stable step into a node.

## Node Types

Most nodes fall into one of four categories:

- LLM nodes: classify, reason, draft, evaluate, summarize.
- Data nodes: search docs, fetch user/account history, retrieve records.
- Action nodes: create ticket, send email, write to database.
- Human nodes: approval, edit, clarification, escalation.

Keep node names action-oriented: `classify_intent`, `search_docs`, `draft_answer`, `human_review`.

## State Design

Put durable raw data in state:

- original input,
- classification result,
- search results,
- generated draft,
- tool/action result,
- final response.

Avoid storing formatted prompts. Build prompts in the node using current state.

## Pattern: Prompt Chain

Use when steps are predetermined:

```text
START -> generate -> check -> improve -> final -> END
```

Use a conditional edge after a validator/checker to skip or continue improvement.

## Pattern: Router

Use when an early classification decides the path:

```text
START -> classify -> {retrieve | action | human_review | answer}
```

Use structured output from the model to populate `state["route"]`, then route with `add_conditional_edges`.

## Pattern: Parallel Fan-Out

Use when independent tasks can run at the same time:

```text
START -> {extract_facts, check_policy, search_docs} -> synthesize -> END
```

Any shared output key needs a reducer.

## Pattern: Orchestrator-Worker

Use when the number of subtasks is dynamic:

```text
START -> plan_sections -> Send(worker per section) -> reduce -> END
```

Use `Send` with a worker-specific state payload and a reducer field for worker outputs.

## Pattern: Evaluator-Optimizer

Use when quality must be checked and improved:

```text
START -> draft -> evaluate -> {revise | END}
```

Keep a max-iteration or remaining-step guard so the graph cannot loop forever.

## Minimal Build Order

1. Write the state schema.
2. Stub the nodes with deterministic code.
3. Wire edges and conditional edges.
4. Compile and invoke with tiny fixtures.
5. Add LangChain model/tool calls inside nodes.
6. Add checkpointing only when you need memory, interrupts, or recovery.
7. Add streaming once the workflow shape is stable.

## Practical Defaults

- Use `TypedDict` for state.
- Use `MessagesState` when the graph is conversational.
- Use `ChatOpenAI` or `init_chat_model` for model calls.
- Use `with_structured_output` for routing/classification.
- Use conditional edges for routing.
- Use `Command` when the node should both update and route.
- Use `create_agent` only when the prebuilt vanilla agent loop is enough.
- Use custom `StateGraph` when you need explicit workflow control.
