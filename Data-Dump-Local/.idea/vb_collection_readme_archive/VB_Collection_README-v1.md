
# Voice Bot — EMI Collections (IDFC First Bank)

Overview
-
This folder contains the assets and orchestration for the voice-based EMI collections flow used by an IDFC First Bank voice assistant. The system uses an LLM to generate conversational text, a fast TTS to speak that text, and an STT to transcribe customer replies; the LLM then consumes the transcript to produce the next response. The flow is implemented as a set of nodes (authenticate → negotiate → oncall_payment) coordinated by `node-traffic-flow.py`.

Architecture & Components
-
- LLM: Produces natural Hinglish/English responses using customer context from the `sample-cust-config.json` file.
- TTS: Converts LLM output to speech during real-time calls.
- STT: Converts customer speech back into text and is fed to the LLM for the next turn.
- Orchestrator: `node-traffic-flow.py` defines nodes, system prompts and action hooks that call internal tools (e.g., send payment link, validate PTP date, set EMI offer flag).

Key Files
-
- Prompts:
	- `prompt_authenticate.txt` — Identity confirmation stage. Must confirm identity before revealing account details.
	- `prompt_negotiate.txt` — Negotiation phase prompts and high-priority guardrails (female voice persona, Two Genders Protocol, tool-first mandate).
	- `prompt_ocop.txt` — On-call payment (OCOP) flow focused on guiding the customer to use the secure payment link; includes mandatory tool triggers and triage logic.
- Flow definition:
	- `node-traffic-flow.py` — Implements `setup_nodes()`, `get_opening()`, `get_negotiation_prompt_file()` and `get_negotiate_actions()` to assemble the node list and action mapping used at runtime.
- Example context & artifacts:
	- `sample-cust-config.json` — Customer-specific variables used to populate prompts and personalize the LLM context (EMI amounts, names, links, flags).
	- `transcript-1.txt`, `transcript-2.txt` — Cleaned transcripts used as examples and references for expected conversational style.

Node Flow Summary
-
1. authenticate
	 - Purpose: Confirm call recipient identity before any sensitive information is shared.
	 - Prompts: `prompt_authenticate.txt`
	 - Tools: `action_customer_authenticated`, `action_terminate_call` (internal, silent calls).

2. negotiate
	 - Purpose: Run the negotiation dialog to capture intent to pay, handle objections, offer EMI options when applicable.
	 - Prompts: `prompt_negotiate.txt` (language/gender guardrails enforced).
	 - Actions: Guidance for on-call payment, validate PTP dates, send/resend payment link, optionally set EMI offer flag.
	 - Behavior: The system follows the Tool-First Mandate — tool triggers are the highest-priority responses and are invoked silently.

3. oncall_payment
	 - Purpose: Payment closer — guide the customer to open and complete payment via the secure link (WhatsApp/SMS), troubleshoot link issues, and confirm payment.
	 - Prompts: `prompt_ocop.txt`
	 - Actions: `action_send_payment_link`, `action_send_deep_payment_link` (conditional), `action_check_payment_status`, `action_terminate_call`.

Persona & Guardrails (important)
-
- Bot persona: female speaker; all bot-first-person Hindi verb forms must be female.
- Customer address: always gender-neutral — use plural/formal `आप` forms; never assume customer gender.
- Language: Hinglish (Hindi in Devanagari for Hindi words, English in Latin script). Keep phrasing natural and conversational.
- Tool-Secrecy: All tool calls (send link, validate PTP, set EMI flag, terminate) are silent internal actions; they must never appear verbatim in spoken output.
- Data Accuracy: All monetary and account values must come from `sample-cust-config.json` or equivalent runtime context — never invent values.

How the LLM context is built
-
1. Load the customer config (e.g., `sample-cust-config.json`) and runtime flags (`total_vs_emi_flag`, `escalation_flag`).
2. Choose the correct prompt file per node and per language/gender mapping (these mappings are handled by `node-traffic-flow.py`).
3. Inject variables (customer name, EMI words, payment link, amounts) into the prompt template.
4. LLM produces the bot utterance (text-only). The orchestrator decides whether a tool must be triggered before/after speaking.

Testing & Examples
-
- Use `transcript-1.txt` and `transcript-2.txt` as sample dialogues to validate LLM output style and adherence to guardrails.
- To test the node orchestration, review `node-traffic-flow.py` and simulate node transitions by providing mock customer replies and the `sample-cust-config.json` context.

Extending or Modifying the Flow
-
- To add or modify behavior, update or add prompt files in the `prompts/TS1ReleaseCollections/` folder and adapt `node-traffic-flow.py` to point to the new templates.
- When adding actions, ensure corresponding internal tool hooks exist and remain silent (the conversational text must not include function call text).
- Keep guardrails intact (gender protocol, language, data sourcing) when modifying prompts.

Notes and Best Practices
-
- Keep prompts short and focused; use the Tool-First mandate to handle link delivery and payment confirmation rather than relying on generated instructions alone.
- Maintain separate prompt variants for male/female bot voices and for Hindi/English language modes; the flow selects the correct variant at runtime.
- Log all tool actions and responses for auditability, but never expose internal logs in spoken responses.

References
-
- Flow definition: `node-traffic-flow.py`
- Prompts: `prompt_authenticate.txt`, `prompt_negotiate.txt`, `prompt_ocop.txt`
- Example data & transcripts: `sample-cust-config.json`, `transcript-1.txt`, `transcript-2.txt`

--
Last updated: 2026-01-06

