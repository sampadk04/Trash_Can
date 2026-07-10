Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.

Expected Conversation Flow by Jarvis Bot ->
"""
I analysed the full **2:31 video**. It is a voice-banking assistant demo in which a customer named **Ravi** talks to **Jarvis**, an AI banking assistant. The conversation starts as a balance inquiry and progressively becomes a transactional workflow: **loan inquiry → foreclosure analysis → impact check → execution preview → explicit confirmation → transaction completion → contextual cross-sell**.

The transcript below is reconstructed from the spoken interaction and the live on-screen transcript. The video is only 832×464 and some text is heavily compressed, but the dialogue and financial figures below are legible with high confidence.

## Full conversation script

### 1. Greeting

**Jarvis:**

> Hi Ravi 👋 How can I help today?

**Ravi:**

> What is the outstanding amount on my loan?

**Jarvis:**

> Your Personal Loan (A/C ...8841) has an outstanding of ₹6,42,003. Your next EMI of ₹21,788 is due on 5 Jul, and about 30 EMIs remain at 11.6% p.a. Anything you'd like to do with it?

---

### 2. Ravi asks to close the loan early

**Ravi:**

> I would like to close my loan early.

The interface classifies/displays this intent as:

> **Close this loan early**

**Jarvis:**

> Happy to help you close it. A bit of good news first — since this is a floating-rate personal loan, there's ₹0 foreclosure charge. The amount to close today is ₹6,42,000, and doing it now saves you roughly ₹74,000 in interest you'd have paid over the remaining EMIs. Your matured FD ₹8,28,403 sitting in Savings ...4382 can cover this comfortably. Your NOC would reach you within 7 working days. Want to go ahead?

---

### 3. Ravi checks the knock-on effect on his finances

**Ravi:**

> Will this affect my SIP balance?

**Jarvis:**

> Good thing to check. After paying ₹6,42,003, about ₹1,86,400 stays in your savings. This comfortably covers your ₹15,000 SIP on the 8th and keeps you above the ₹25,000 minimum balance — so no missed SIP and no non-maintenance charge. You're all clear to proceed.

This is an important part of the demo: Jarvis is not merely executing the loan transaction. It is performing a **cross-product impact analysis** across the customer's:

* personal loan,
* savings account,
* matured FD proceeds,
* scheduled SIP,
* minimum-balance requirement.

---

### 4. Ravi decides to proceed

**Ravi:**

> Let's proceed with my foreclosure then.

The interface translates this into the action intent:

> **Proceed to foreclose**

**Jarvis:**

> Here's what I'll do, please confirm: Pay from Savings ...4382 — ₹6,42,000. Close Personal Loan ...8841 (5 Jul EMI ₹21,788 stops). NOC: To your registered email, within 7 working days.

At this point, the UI presents explicit action choices, including approximately:

**Confirm & pay ₹6,42,000**
**Change source account**
**Cancel**

This is effectively a **pre-transaction confirmation checkpoint**.

---

### 5. Ravi confirms the transaction

**Ravi:**

> Perfect, I confirm.

The interface displays the execution action as:

> **Confirm & pay ₹6,42,000**

**Jarvis:**

> Done ✅ Your foreclosure request is placed (Ref: FC-2026-6841). The amount is debited, the loan will show as closed shortly, and your NOC will arrive within 7 working days. Your 5 Jul EMI is cancelled, and ₹1,86,400 remains in savings — enough for your SIP and minimum balance. One small thing for later, no rush: your card runs at 90–96% of its limit most months, so you're pre-approved for a higher limit card. Happy to show you whenever you like.

---

# What is happening functionally

The video demonstrates much more than a simple chatbot conversation.

### Stage 1: Information retrieval

Ravi asks a general question:

> “What is the outstanding amount on my loan?”

Jarvis resolves which loan he means and retrieves:

* account ending **8841**,
* outstanding amount **₹6,42,003**,
* EMI **₹21,788**,
* next due date **5 July**,
* approximately **30 EMIs remaining**,
* interest rate **11.6% p.a.**

The user does not have to manually navigate to a loan page or provide an account number.

### Stage 2: Financial simulation before action

When Ravi says he wants to close the loan, Jarvis does not immediately execute anything. It calculates and explains:

* foreclosure fee: **₹0**,
* current closure amount: approximately **₹6.42 lakh**,
* projected interest saving: approximately **₹74,000**,
* a viable funding source: matured FD proceeds in savings,
* NOC delivery SLA: **7 working days**.

This is essentially a **personalized financial decision-support step**.

### Stage 3: Constraint and dependency checking

Ravi raises a concern about the SIP.

Jarvis performs what appears to be a forward-looking liquidity check:

[
₹8,28,403 - ₹6,42,003 \approx ₹1,86,400
]

It then checks that the remaining liquidity can accommodate:

[
₹15,000\text{ SIP}
]

while retaining at least:

[
₹25,000\text{ minimum balance}
]

The assistant therefore assures Ravi that neither the SIP nor the account's minimum-balance requirement will be disrupted.

### Stage 4: Action plan before commitment

Before taking an irreversible financial action, Jarvis explicitly summarizes:

**Source:** Savings account ...4382
**Amount:** ₹6,42,000
**Destination/action:** Foreclose Personal Loan ...8841
**Immediate consequence:** 5 Jul EMI stops
**Post-action document:** NOC by registered email within 7 working days

Only then does it request confirmation.

### Stage 5: Transaction execution and post-transaction state

After Ravi says:

> “Perfect, I confirm.”

Jarvis executes or simulates the execution of the workflow and returns:

* transaction/reference ID,
* debit confirmation,
* upcoming EMI cancellation,
* loan closure status,
* NOC timeline,
* remaining savings balance.

This closes the original user journey completely.

### Stage 6: Contextual cross-sell

Only after the foreclosure workflow is complete, Jarvis introduces another observation:

> the customer's card is regularly running at approximately 90–96% utilization.

It then mentions eligibility for a higher-limit card.

The design intent appears to be **post-service contextual cross-selling**: the assistant first completes the user's requested job, then makes a low-pressure, data-driven offer rather than interrupting the main task.

## Overall conversational structure

The flow can be represented as:

```text
Loan enquiry
    ↓
Retrieve loan details
    ↓
User expresses foreclosure intent
    ↓
Calculate foreclosure cost + savings
    ↓
Identify appropriate funding source
    ↓
User raises SIP/liquidity concern
    ↓
Run post-payment liquidity simulation
    ↓
User decides to proceed
    ↓
Present explicit transaction summary
    ↓
Obtain confirmation
    ↓
Execute foreclosure
    ↓
Report final financial state
    ↓
Contextual credit-card upsell
```

The strongest aspect of the demo is that Jarvis maintains **cross-domain financial context** throughout the conversation. It reasons across lending, deposits, savings liquidity, investments, balance requirements, document fulfilment, and credit-card utilisation without forcing the user to move between separate product flows.

"""


