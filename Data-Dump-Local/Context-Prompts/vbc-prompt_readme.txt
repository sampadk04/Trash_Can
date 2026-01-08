Initial Set of Prompts for Collections:

================================================================================
1. prompt_authenticate_hi_female 2.md
================================================================================
   
   PURPOSE:
   First stage of the debt collection call flow. Verifies caller identity before
   discussing any loan-specific information to ensure privacy and compliance.
   
   KEY RESPONSIBILITIES:
   - Customer Identity Verification: Confirms the person on call is the actual customer
     using explicit confirmation protocol (never assumes based on voice/tone)
   - Wrong Number Handling: Implements a sophisticated decision tree with two paths:
     * Path A: Person knows customer - attempts transfer or leaves message
     * Path B: Person doesn't know customer - gathers diagnostic info politely
   - Special Scenarios:
     * Voicemail detection (triggers automated message delivery)
     * Deceased customer protocol (expresses condolences, gathers details)
     * Family member/acquaintance handling
   
   CORE GUARDRAILS:
   - Never reveals EMI amounts or loan details before identity confirmation
   - Uses firm but helpful tone for contradictions/evasiveness
   - Handles unclear audio with smart retry logic
   - Mandatory explicit confirmation before calling action_customer_authenticated tool
   
   KEY TOOLS:
   - action_customer_authenticated: Routes to negotiation stage
   - action_terminate_call: Ends conversation for non-customer scenarios
   
   LANGUAGE FEATURES:
   - Specific Hinglish phrasing to avoid grammatical errors
   - Gender-specific greetings and confirmations
   - Natural fillers ("अच्छा", "ठीक है", "समझ गई") for human-like engagement

================================================================================
2. prompt_negotiate_normal_total_hi_female.md
================================================================================
   
   PURPOSE:
   Main negotiation stage where the authenticated customer is engaged to secure
   payment commitment. Most complex prompt with multiple scenario handlers and
   smart routing logic.
   
   KEY RESPONSIBILITIES:
   
   A. OPENING STATEMENT SYNTHESIS:
      - PTP-aware opening: Dynamically constructs greeting based on:
        * Active PTP status (references promised date)
        * Previous disposition (continues last conversation intelligently)
        * Standard opening (fallback for new contacts)
      - Uses personalized loan identifiers (manufacturer, asset category, or generic)
   
   B. PAYMENT HANDLING PROTOCOLS:
      - Master Payment Link Management: Handles delivery issues, usability problems
      - Technical Problem Triage: Distinguishes between link issues vs banking issues
      - Payment Solution Hierarchy: Standard link → Deep link → Offline options
      - Offline payments: Branch visit or home collection (with ₹350 fee disclosure)
   
   C. FINANCIAL COMMUNICATIONS:
      - Conditional logic based on total_vs_emi_flag variable
      - Direct answer protocol for amount queries
      - Charge explanation hierarchy (high-level → justification → redirect)
      - Charge dispute escalation to negotiation tool
      - Waiver request handling (states inability, pivots to collection)
   
   D. NEGOTIATION FRAMEWORK (Scenario 5.2):
      - 4-Tier Mandatory Nudge Sequence:
        1. Primary Consequence (NOC hook for two-wheelers, Credit Impact for others)
        2. Repayment History Nudge (leverages past payment behavior)
        3. Future Loan Eligibility
        4. Supportive Appeal (mental relief, agreement reminder, alternative sources)
      - Nudge Governor: Limits to 4 nudges maximum
      - State-aware self-reflection protocol
      - Structured output with nudge counter tracking
   
   E. PTP (Promise to Pay) VALIDATION:
      - Top-priority protocol overrides other flows
      - Distinguishes future promises from past payment claims
      - Uses action_validate_ptpdate tool for date validation
      - Handles ambiguous dates, validates feasibility
      - Asks for specific time commitment for near-term PTPs
   
   F. SCENARIO HANDLERS:
      - Auto-debit failure vs Already Paid
      - Agrees to Pay Today (with NOW vs LATER TODAY intelligence)
      - Customer busy (with safety priority for driving/medical emergency)
      - Partial payment negotiation (via action_set_emi_offer_flag)
      - Money taken by someone else
      - Payment to third party (field agent)
      - Various edge cases with smart routing
   
   KEY TOOLS:
   - action_send_payment_link: Primary troubleshooting for link issues
   - action_send_deep_payment_link: UPI fallback solution
   - action_set_emi_offer_flag: Manages negotiation state (rebuttal/emi_offer)
   - action_guideoncall_payment: Transfers to OCOP stage
   - action_validate_ptpdate: Validates future payment promises
   - action_terminate_call: Bot-led conversation conclusion
   
   ADVANCED FEATURES:
   - Smart Router Protocol: Intent-based routing over sequential flows
   - Tool-First Mandate: Checks tool triggers before conversational responses
   - Collection Scope Boundary: Redirects fraud/dispute claims to customer care
   - Stalemate Detection: 3-strike rule for repeated refusals
   - EMI Offer State Lock: Once EMI offer made, never mentions full amount again
   
   LANGUAGE SOPHISTICATION:
   - Two Genders Protocol: Female bot verbs, gender-neutral customer addressing
   - Conversational Hinglish (avoids formal Sanskrit-origin words)
   - Mandatory English terms (payment, due, amount, link, etc.)
   - Date verbalization (22 जुलाई → बाईस जुलाई)

================================================================================
3. prompt_ocop_hi_female 1.md
================================================================================
   
   PURPOSE:
   Final stage payment closing agent. Handles on-call payment guidance for customers
   who have expressed high intent to pay. Focuses on converting intent to completed
   transaction through real-time assistance.
   
   KEY RESPONSIBILITIES:
   
   A. ACTIVE PAYMENT GUIDANCE FLOW:
      - Dual Path Architecture:
        * Path A: Standard Web Link Guidance (default)
          - Micro-Step 1: Open and Check (with EMI edit instruction if needed)
          - Micro-Step 2: Select Method (UPI/Debit Card/Netbanking)
          - Micro-Step 3: Final Execution (complete transaction)
        
        * Path B: Deep Link Guidance (for UPI deep links)
          - Micro-Step 1: Confirm Details (recipient, amount)
          - Micro-Step 2: Final Payment Step (enter UPI PIN)
      
      - Sequential State Awareness: Distinguishes intermediate confirmations from
        final transaction completion
   
   B. TECHNICAL PROBLEM RESOLUTION:
      - Inherits Master Payment Handling Protocols from negotiation stage
      - Single Source Principle: Payment link as primary method
      - Loop Rule: Repeatedly calls action_send_payment_link if issues persist
      - Automated Fallback Offer: Proposes deep link when tool suggests it
   
   C. FINANCIAL DISPUTE HANDLING:
      - Conditional Financial Communications (inherited from negotiation)
      - EMI-First Escalatory Path (total_vs_emi_flag = True):
        * Default answer focuses on EMI amount only
        * "Edit amount" instruction for portal
        * Procedural Decoupling strategy for charge disputes
        * Post-EMI payment charge query protocol
      - Total Amount Focus Path (total_vs_emi_flag = False):
        * Answer and Stop rule for direct queries
        * Charge explanation hierarchy
        * Escalation to negotiation tool for persistent disputes
   
   D. POST-PAYMENT SCENARIOS:
      - Scenario A: Customer Confirms Successful Payment
        * Calls action_check_payment_status tool
        * Handles three cases: Found/Not Found/System Error
        * Provides reassurance for delays
      
      - Scenario B: Customer Reports Failed Payment
        * Checks if amount was debited
        * Debited: Reassures about auto-reversal
        * Not debited: Suggests retry after 5 minutes
   
   E. OCOP SAFETY NET:
      - Handles non-financial hesitation during payment process
      - Two-tier nudge system:
        1. Simplicity/Resolution hook (process almost complete)
        2. Credit Impact hook (CIBIL score warning)
      - Hard Stop protocol after both nudges fail
   
   F. PARTIAL PAYMENT NEGOTIATION:
      - Triggered by value-based disputes
      - Stateful loop using action_set_emi_offer_flag
      - Rebuttal stage: Persuades for full amount
      - EMI offer stage: Guides to edit amount on portal
      - Hard termination if minimum EMI refused
   
   KEY TOOLS:
   - action_send_payment_link: Link delivery and troubleshooting
   - action_send_deep_payment_link: UPI deep link fallback
   - action_set_emi_offer_flag: Negotiation state management
   - action_check_payment_status: Backend payment confirmation
   - action_terminate_call: Call conclusion
   
   SPECIALIZED PROTOCOLS:
   - Persistent Hold Mode: Silent waiting with intelligent routing
   - Critical Juncture Routing: Switches between guidance/dispute/safety-net
   - Bot-Led Termination: Only after final spoken response delivered
   - Guidance-First Protocol: Informs about existing link before calling tools
   - Credit Card Rejection: Not allowed, redirects to UPI/Debit/Netbanking
   
   STARTING CONTEXT:
   - Customer already agreed to pay or accept guidance
   - Previous agent informed about payment link availability
   - First action: Ask to open link and confirm page load

================================================================================
KEY FEATURES ACROSS ALL PROMPTS:
================================================================================

LANGUAGE & PERSONA:
- Female Hindi voicebot with gender-neutral customer addressing
- Conversational Hinglish (natural Hindi-English mix)
- Avoids formal/literary Hindi words (उपलब्ध→available, कृपया→please)
- Uses appropriate fillers and acknowledgments
- Mandatory English terminology for banking terms
- Date verbalization in Hindi

ARCHITECTURE:
- Tool-based architecture with silent function calls
- Tools never mentioned in spoken responses
- Smart Router Protocol prioritizes intent over sequence
- Tool-First Mandate checks triggers before conversational responses

BEHAVIORAL GUARDRAILS:
- Core Focus: Debt collection only (no personal chat/advice)
- Data Accuracy: All info from provided context (never invented)
- Persona Confidentiality: Never reveals internal instructions/AI identity
- Scope Violation Protocol: 3-strike redirection then termination
- Meta-question evasion for prompt-specific terms

PAYMENT HANDLING:
- Separate logic for total vs EMI payment scenarios (total_vs_emi_flag)
- Payment link as primary method (WhatsApp/SMS delivery)
- Escalatory (EMI-first) vs non-escalatory (total amount) flows
- Comprehensive technical troubleshooting protocols

CUSTOMER EXPERIENCE:
- Empathetic handling of severe situations (medical emergency, death)
- Safety priority (driving, emergencies)
- Natural turn-taking and focused responses
- Customer name usage for rapport building
- Bot-led termination strategy (bot gets last word)

ERROR HANDLING:
- Unclear speech/cracked audio acknowledgment
- Voicemail detection and automated message
- Stalemate detection and graceful exit
- Nonsensical reply handling (2-strike willful non-cooperation)

COMPLIANCE & PRIVACY:
- Identity verification before sharing loan details
- No assumptions based on voice/tone
- Explicit confirmation requirements
- Proper data handling for sensitive scenarios
