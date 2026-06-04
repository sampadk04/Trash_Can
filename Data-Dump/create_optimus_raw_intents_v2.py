import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw-intents" / "optimus-raw-intents.csv"
OUTPUT = ROOT / "data" / "raw-intents" / "optimus-raw-intents-v2.csv"

NLU_COLUMNS = [
    "nlu_intent",
    "nlu_entities",
    "nlu_examples",
    "nlu_disambiguation_hint",
]

ALLOWED_DUPLICATE_INTENT_GROUPS = [
    {"ADD_PAYEE", "ADD_BENEFICIARY"},
    {"VIEW_PAYEE", "VIEW_BENEFICIARY"},
]

ROW_OVERRIDES = {
    "EMAIL_CHANGE": {
        "nlu_intent": "update_email",
        "entities": {
            "action": "update",
            "product": "profile",
            "feature": "email",
            "profile_attribute": "email",
            "service_type": "profile_update",
        },
    },
    "VIEW_INSTANT_SERVICES": {
        "nlu_intent": "view_instant_services",
        "entities": {
            "action": "view",
            "product": "instant_services",
            "feature": "instant_services",
            "service_type": "service_request",
        },
    },
    "CC_SETTLEMENT": {
        "nlu_intent": "settle_credit_card_dues",
        "entities": {
            "action": "settle",
            "product": "credit_card",
            "feature": "credit_card_dues",
            "card_type": "credit_card",
        },
    },
    "PAY_BILL": {
        "nlu_intent": "pay_bill",
        "entities": {
            "action": "pay",
            "product": "bill_payment",
            "feature": "bill",
            "biller_type": "generic_bill",
        },
    },
    "VIEW_UPDATE_PAN": {
        "nlu_intent": "update_pan_details",
        "entities": {
            "action": "update",
            "product": "account",
            "feature": "pan_details",
            "profile_attribute": "pan",
            "service_type": "profile_update",
        },
    },
    "ME2ME_TRANSFER": {
        "nlu_intent": "transfer_me2me",
        "entities": {
            "action": "transfer",
            "product": "account",
            "feature": "me2me",
            "payment_type": "me2me_transfer",
        },
    },
}

ACTION_WORDS = {
    "access",
    "activate",
    "add",
    "apply",
    "assess",
    "avail",
    "block",
    "book",
    "buy",
    "calculate",
    "cancel",
    "change",
    "check",
    "close",
    "complete",
    "contact",
    "convert",
    "create",
    "delete",
    "deregister",
    "discover",
    "download",
    "enable",
    "explore",
    "find",
    "foreclose",
    "get",
    "increase",
    "invest",
    "locate",
    "make",
    "manage",
    "modify",
    "open",
    "pay",
    "place",
    "plan",
    "recharge",
    "redeem",
    "refer",
    "remove",
    "replace",
    "request",
    "save",
    "schedule",
    "send",
    "set",
    "settle",
    "share",
    "show",
    "start",
    "stop",
    "switch",
    "track",
    "transfer",
    "unblock",
    "update",
    "use",
    "view",
    "withdraw",
}


def clean(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def slug(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def text_for(row: pd.Series) -> str:
    parts = [
        clean(row.get("intent")),
        clean(row.get("title")),
        clean(row.get("label")),
        clean(row.get("description")),
        clean(row.get("tags")),
        clean(row.get("product_category")),
        clean(row.get("sr_category")),
    ]
    return " ".join(parts).lower()


def first_match(text: str, candidates):
    for key, value in candidates:
        if key in text:
            return value
    return ""


def has_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase.lower()).replace(r"\ ", r"\s+")
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text.lower()) is not None


def field_text(row: pd.Series, *fields: str) -> str:
    return " ".join(clean(row.get(field)) for field in fields).lower()


def compact_subject(value: str) -> str:
    value = slug(value)
    tokens = [token for token in value.split("_") if token and token not in ACTION_WORDS]
    subject = "_".join(tokens)
    replacements = {
        "my": "",
        "how": "",
        "do": "",
        "i": "",
        "can": "",
        "what": "",
        "is": "",
        "are": "",
        "for": "",
        "of": "",
        "to": "",
        "in": "",
        "the": "",
        "a": "",
        "an": "",
        "your": "",
    }
    tokens = [token for token in subject.split("_") if token and token not in replacements]
    return re.sub(r"_+", "_", "_".join(tokens)).strip("_")


def primary_subject(row: pd.Series) -> str:
    label = clean(row.get("label"))
    title = clean(row.get("title"))
    intent = clean(row.get("intent"))
    for candidate in [label, title, intent]:
        subject = compact_subject(candidate)
        if subject:
            return subject
    return slug(intent)


def infer_action(intent: str, text: str) -> str:
    if "SETTLEMENT" in intent or " settle " in f" {text} ":
        return "settle"
    if "TRANSFER" in intent:
        return "transfer"
    if "CHANGE" in intent or "UPDATE" in intent:
        return "update"
    if intent.endswith("_CLOSURE") or " close " in f" {text} ":
        return "close"
    if "foreclosure" in intent.lower() or " foreclose " in f" {text} ":
        return "foreclose"

    prefix_map = [
        ("DOWNLOAD_", "download"),
        ("TRACK_", "track"),
        ("VIEW_", "view"),
        ("SHOW_", "view"),
        ("PAY_", "pay"),
        ("RECHARGE_", "recharge"),
        ("BOOK_", "book"),
        ("OPEN_", "open"),
        ("CREATE_", "open"),
        ("ADD_", "add"),
        ("UPDATE_", "update"),
        ("CHANGE_", "update"),
        ("SET_", "set"),
        ("SETUP_", "set"),
        ("ENABLE_", "enable"),
        ("MANAGE_", "manage"),
        ("BLOCK_", "block"),
        ("UNBLOCK_", "unblock"),
        ("ACTIVATE_", "activate"),
        ("REPLACE_", "replace"),
        ("APPLY_", "apply"),
        ("INVEST_", "invest"),
        ("REDEEM_", "redeem"),
        ("TRANSFER_", "transfer"),
        ("REMOVE_", "remove"),
        ("DEREGISTER_", "remove"),
        ("STOP_", "stop"),
        ("BUY_", "buy"),
        ("CALCULATE_", "calculate"),
        ("CONVERT_", "convert"),
        ("LOCATE_", "locate"),
        ("CONTACT_", "contact"),
        ("REFER_", "refer"),
    ]
    for prefix, action in prefix_map:
        if intent.startswith(prefix):
            return action

    action_words = [
        "download",
        "track",
        "view",
        "check",
        "pay",
        "recharge",
        "book",
        "open",
        "create",
        "add",
        "update",
        "change",
        "set",
        "enable",
        "manage",
        "block",
        "unblock",
        "activate",
        "replace",
        "apply",
        "invest",
        "redeem",
        "transfer",
        "remove",
        "stop",
        "buy",
        "calculate",
        "convert",
        "locate",
        "contact",
        "foreclose",
    ]
    return first_match(text, [(word, "view" if word == "check" else word) for word in action_words]) or "view"


def infer_product(text: str) -> str:
    product_candidates = [
        ("net worth", "networth"),
        ("networth", "networth"),
        ("easy buy", "easy_buy_card"),
        ("credit card", "credit_card"),
        (" cc ", "credit_card"),
        ("debit card", "debit_card"),
        ("atm card", "debit_card"),
        ("pay later", "pay_later"),
        ("revolving credit", "pay_later"),
        ("personal loan", "personal_loan"),
        ("two wheeler loan", "two_wheeler_loan"),
        ("two-wheeler loan", "two_wheeler_loan"),
        ("home loan", "home_loan"),
        ("mortgage loan", "mortgage_loan"),
        ("consumer loan", "consumer_loan"),
        ("vehicle loan", "vehicle_loan"),
        ("loan", "loan"),
        ("fixed deposit", "fixed_deposit"),
        (" fd ", "fixed_deposit"),
        ("recurring deposit", "recurring_deposit"),
        (" rd ", "recurring_deposit"),
        ("fcnr", "fcnr_deposit"),
        ("gift city", "gift_city_account"),
        ("savings account", "savings_account"),
        ("account", "account"),
        ("upi", "upi"),
        ("vpa", "upi"),
        ("qr", "upi_qr"),
        ("payee", "payee"),
        ("beneficiary", "payee"),
        ("cheque book", "cheque_book"),
        ("chequebook", "cheque_book"),
        ("welcome kit", "welcome_kit"),
        ("mutual fund", "mutual_fund"),
        (" mf", "mutual_fund"),
        ("sip", "sip"),
        ("sgb", "sovereign_gold_bond"),
        ("sovereign gold", "sovereign_gold_bond"),
        ("ipo", "ipo"),
        ("ncd", "ncd"),
        ("stock", "stock_portfolio"),
        ("investment", "investment"),
        ("insurance", "insurance"),
        ("health cover", "health_insurance"),
        ("health insurance", "health_insurance"),
        ("motor insurance", "motor_insurance"),
        ("life cover", "life_insurance"),
        ("term insurance", "term_insurance"),
        ("biometric", "biometric_login"),
        ("aadhaar", "aadhaar"),
        ("cibil", "cibil"),
        ("customer id", "customer_id"),
        ("relationship manager", "relationship_manager"),
        ("service request", "service_request"),
        ("settings", "settings"),
        ("profile", "profile"),
        ("hotel", "hotel_booking"),
        ("fastag", "fastag"),
        ("dth", "dth"),
        ("electricity", "electricity_bill"),
        ("postpaid", "postpaid_bill"),
        ("school fees", "school_fees"),
        ("college fees", "college_fees"),
        ("cylinder", "gas_cylinder"),
    ]
    return first_match(f" {text} ", product_candidates) or "banking_service"


def infer_feature(row: pd.Series, product: str) -> str:
    primary_text = field_text(row, "intent", "title", "label")
    subject = primary_subject(row)
    feature = first_match(
        primary_text,
        [
            ("net worth", "networth"),
            ("networth", "networth"),
            ("loan details", "loan_details"),
            ("loan document", "loan_documents"),
            ("loan application", "loan_application"),
            ("loan emi", "loan_emi"),
            ("credit card outstanding", "credit_card_outstanding"),
            ("outstanding amount", "outstanding_amount"),
            ("statement date", "statement_date"),
            ("billing cycle", "billing_cycle"),
            ("credit card statement", "credit_card_statement"),
            ("debit card controls", "debit_card_controls"),
            ("credit card controls", "credit_card_controls"),
            ("card controls", "card_controls"),
            ("card privileges", "card_privileges"),
            ("reward points", "reward_points"),
            ("airport lounge", "airport_lounge"),
            ("payment options", "payment_options"),
            ("balance transfer", "balance_transfer"),
            ("relationship manager", "relationship_manager"),
            ("customer id", "customer_id"),
            ("service request", "service_request"),
            ("instant services", "instant_services"),
            ("biometric", "biometric_login"),
            ("checksum", "checksum"),
            ("salary booster", "salary_booster"),
            ("refer and earn", "refer_and_earn"),
            ("marketing", "marketing_communications"),
            ("gift city holdings", "gift_city_holdings"),
            ("gift city savings", "gift_city_savings_account"),
            ("fcnr deposit", "fcnr_deposit"),
            ("3-in-1 account", "three_in_one_account"),
            ("3 in 1 account", "three_in_one_account"),
            ("credit card against fd", "credit_card_against_fd"),
            ("creditpro", "creditpro_balance_transfer"),
            ("pay later foreclosure", "pay_later_foreclosure"),
            ("loan foreclosure", "loan_foreclosure"),
            ("foreclose my loan", "loan_foreclosure"),
            ("re-kyc", "re_kyc"),
            ("rekyc", "re_kyc"),
            ("demat account", "demat_account"),
            ("e-voting", "e_voting"),
            ("vpa", "upi_vpa"),
            ("qr code", "upi_qr"),
        ],
    )
    return feature or subject or product


def infer_service_type(primary_text: str, text: str) -> str:
    return first_match(
        f" {primary_text} {text} ",
        [
            ("delivery", "delivery_tracking"),
            ("deliverable", "delivery_tracking"),
            ("service request", "service_request"),
            ("complaint", "service_request"),
            ("foreclosure", "foreclosure"),
            ("foreclose", "foreclosure"),
            ("profile", "profile_update"),
            ("marketing", "marketing_opt_out"),
            ("customer care", "customer_care"),
            ("call back", "callback"),
            ("call assistance", "callback"),
            ("device", "device_management"),
            ("settings", "settings_management"),
        ],
    )


def infer_biller_type(primary_text: str) -> str:
    return first_match(
        primary_text,
        [
            ("broadband", "broadband"),
            ("gas bill", "gas"),
            ("landline", "landline"),
            ("municipal tax", "municipal_tax"),
            ("rent", "rent"),
            ("utility", "utilities"),
            ("electricity", "electricity"),
            ("postpaid", "postpaid_mobile"),
            ("school fees", "school_fees"),
            ("college fees", "college_fees"),
            ("subscription", "subscription"),
            ("dth", "dth"),
            ("fastag", "fastag"),
            ("cylinder", "gas_cylinder"),
            ("insurance premium", "insurance_premium"),
        ],
    )


def infer_investment_goal(primary_text: str) -> str:
    return first_match(
        primary_text,
        [
            ("child", "child_education"),
            ("education", "child_education"),
            ("car goal", "car"),
            ("home goal", "home"),
            ("vacation", "vacation"),
            ("wedding", "wedding"),
            ("financial goals", "financial_goals"),
            ("savings goal", "savings_goal"),
            ("investment goal", "investment_goal"),
        ],
    )


def infer_investment_mode(primary_text: str) -> str:
    return first_match(
        primary_text,
        [
            ("quick invest", "quick_invest"),
            ("lump sum", "lumpsum"),
            ("lumpsum", "lumpsum"),
            ("sip", "sip"),
            ("nfo", "nfo"),
            ("asba", "asba"),
            ("recommendation", "recommendations"),
            ("curated", "curated"),
            ("handpicked", "handpicked"),
        ],
    )


def infer_insurance_type(primary_text: str) -> str:
    return first_match(
        primary_text,
        [
            ("health", "health"),
            ("motor", "motor"),
            ("life", "life"),
            ("term", "term"),
            ("two wheeler", "two_wheeler"),
            ("car insurance", "car"),
            ("maternity", "maternity"),
            ("ulip", "ulip"),
            ("premium", "premium"),
            ("ideal cover", "ideal_cover"),
            ("add-on", "add_on"),
            ("long-term", "long_term"),
            ("family", "family"),
        ],
    )


def infer_document_type(text: str) -> str:
    return first_match(
        text,
        [
            ("capital gain report", "capital_gain_report"),
            ("portfolio statement", "portfolio_statement"),
            ("holding statement", "holding_statement"),
            ("holdings statement", "holding_statement"),
            ("mutual fund report", "mutual_fund_report"),
            ("investment portfolio report", "investment_portfolio_report"),
            ("sip", "sip_report"),
            ("account statement", "account_statement"),
            ("credit card statement", "credit_card_statement"),
            ("tds certificate", "tds_certificate"),
            ("interest certificate", "interest_certificate"),
            ("loan document", "loan_document"),
            ("loan agreement", "loan_document"),
            ("welcome letter", "welcome_letter"),
            ("certificate", "certificate"),
            ("statement", "statement"),
            ("report", "report"),
            ("document", "document"),
        ],
    )


def infer_payment_type(text: str) -> str:
    return first_match(
        text,
        [
            ("rtgs", "rtgs"),
            ("neft", "neft"),
            ("imps", "imps"),
            ("mobile number", "pay_to_mobile"),
            ("pay to mobile", "pay_to_mobile"),
            ("upi", "upi"),
            ("card bill", "credit_card_bill"),
            ("credit card bill", "credit_card_bill"),
            ("loan emi", "loan_emi"),
            ("electricity", "electricity_bill"),
            ("postpaid", "postpaid_bill"),
            ("school fees", "school_fees"),
            ("college fees", "college_fees"),
            ("subscription", "subscription"),
            ("dth", "dth"),
            ("fastag", "fastag"),
            ("canadian dollars", "cad"),
            ("australian dollars", "aud"),
            ("singapore dollars", "sgd"),
            ("pay abroad", "international_transfer"),
            ("nro to nre", "nro_to_nre_transfer"),
            ("between my accounts", "me2me_transfer"),
            ("me2me", "me2me_transfer"),
        ],
    )


def infer_entities(row: pd.Series, action: str, product: str, feature: str, text: str) -> dict:
    entities = {"action": action, "product": product, "feature": feature}
    intent = clean(row.get("intent")).upper()
    primary_text = field_text(row, "intent", "title", "label")

    service_type = infer_service_type(primary_text, text)
    if service_type:
        entities["service_type"] = service_type

    biller_type = infer_biller_type(primary_text)
    if biller_type:
        entities["biller_type"] = biller_type

    investment_goal = infer_investment_goal(primary_text)
    if investment_goal:
        entities["investment_goal"] = investment_goal

    investment_mode = infer_investment_mode(primary_text)
    if investment_mode:
        entities["investment_mode"] = investment_mode

    insurance_type = infer_insurance_type(primary_text)
    if insurance_type:
        entities["insurance_type"] = insurance_type

    if service_type == "foreclosure" and product == "pay_later":
        entities["feature"] = "pay_later_foreclosure"
    elif service_type == "foreclosure" and product == "loan":
        entities["feature"] = "loan_foreclosure"

    if "credit_card" in product or "credit card" in primary_text:
        entities["card_type"] = "credit_card"
    elif "debit_card" in product or "debit card" in primary_text or "atm card" in primary_text:
        entities["card_type"] = "debit_card"

    if "temporary" in primary_text or "temporarily" in primary_text:
        entities["status"] = "temporary"
    if "permanent" in primary_text or "permanently" in primary_text or intent.endswith("_PERMANENT"):
        entities["status"] = "permanent"
    if "active" in text and action == "view":
        entities["status"] = "active_or_blocked"

    if "unbilled transaction" in text:
        entities["transaction_status"] = "unbilled"
    elif "billed transaction" in text:
        entities["transaction_status"] = "billed"
    elif "pending transaction" in text:
        entities["transaction_status"] = "pending"
    elif "recent transaction" in text or "mini statement" in text:
        entities["transaction_status"] = "recent"

    if "atm withdrawal" in text or "atm withdrawals" in text:
        entities["limit_type"] = "atm_withdrawal"
    elif "credit limit" in text or "available limit" in text:
        entities["limit_type"] = "credit_limit"
    elif "overdraft limit" in text:
        entities["limit_type"] = "overdraft_limit"
    elif "billing cycle" in text:
        entities["limit_type"] = "billing_cycle"

    if "domestic" in text:
        entities["usage_scope"] = "domestic"
    elif "international" in text or "abroad" in text or "overseas" in text:
        entities["usage_scope"] = "international"

    if action == "download":
        document_type = infer_document_type(text)
    elif any(word in primary_text for word in ["statement", "certificate", "report", "document"]):
        document_type = infer_document_type(primary_text)
    else:
        document_type = ""
    if document_type:
        entities["document_type"] = document_type

    payment_type = infer_payment_type(primary_text) if action in {"pay", "recharge", "transfer"} else ""
    if action == "transfer" and not payment_type:
        payment_type = "fund_transfer"
    if payment_type:
        entities["payment_type"] = payment_type

    if "loan application" in primary_text:
        entities["loan_type"] = "loan_application"
    elif "home loan" in primary_text:
        entities["loan_type"] = "home_loan"
    elif "personal loan" in primary_text:
        entities["loan_type"] = "personal_loan"
    elif "two wheeler" in primary_text or "two-wheeler" in primary_text:
        entities["loan_type"] = "two_wheeler_loan"
    elif "mortgage loan" in primary_text:
        entities["loan_type"] = "mortgage_loan"
    elif "pay later" in primary_text:
        entities["loan_type"] = "pay_later"
    elif "loan" in primary_text or product.endswith("_loan") or product == "loan":
        entities["loan_type"] = "loan"

    if "savings account" in text:
        entities["account_type"] = "savings_account"
    elif "3-in-1" in text or "3 in 1" in text:
        entities["account_type"] = "three_in_one_account"
    elif "gift city" in text:
        entities["account_type"] = "gift_city_account"
    elif "nro to nre" in text:
        entities["account_type"] = "nro_nre"

    if "fixed deposit" in text or " fd " in f" {text} ":
        entities["deposit_type"] = "fixed_deposit"
    elif "recurring deposit" in text or " rd " in f" {text} ":
        entities["deposit_type"] = "recurring_deposit"
    elif "fcnr" in text:
        entities["deposit_type"] = "fcnr_deposit"

    fund_house = ""
    for phrase, value in [
        ("sbi", "sbi"),
        ("hdfc", "hdfc"),
        ("icici", "icici"),
        ("franklin", "franklin"),
        ("tata", "tata"),
        ("motilal", "motilal_oswal"),
        ("uti", "uti"),
        ("aditya birla", "aditya_birla"),
        ("bajaj", "bajaj_finserv"),
        ("canara", "canara_robeco"),
        ("groww", "groww"),
        ("hsbc", "hsbc"),
        ("lic", "lic"),
        ("trust", "trust"),
    ]:
        if has_phrase(primary_text, phrase):
            fund_house = value
            break
    if fund_house:
        entities["fund_house"] = fund_house

    fund_category = first_match(
        primary_text,
        [
            ("large & mid cap", "large_mid_cap"),
            ("large and mid cap", "large_mid_cap"),
            ("flexi cap", "flexi_cap"),
            ("small cap", "small_cap"),
            ("mid cap", "mid_cap"),
            ("quant", "quant"),
            ("elss", "elss"),
            ("tax saving", "tax_saving"),
            ("equity", "equity"),
            ("bond", "bond"),
            ("it sector", "it_sector"),
            ("fintech", "banking_and_fintech"),
            ("focused", "focused"),
            ("curated", "curated"),
            ("handpicked", "handpicked"),
        ],
    )
    if fund_category:
        entities["fund_category"] = fund_category

    if "reward" in text:
        entities["benefit_type"] = "reward_points"
    elif "airport lounge" in text:
        entities["benefit_type"] = "airport_lounge"

    if "nominee" in primary_text:
        entities["profile_attribute"] = "nominee"
    elif "email" in primary_text:
        entities["profile_attribute"] = "email"
    elif "mobile" in primary_text:
        entities["profile_attribute"] = "mobile"
    elif "address" in primary_text:
        entities["profile_attribute"] = "address"
    elif "aadhaar" in primary_text:
        entities["profile_attribute"] = "aadhaar"
    elif "cibil" in primary_text:
        entities["profile_attribute"] = "cibil"

    if "delivery" in text or "deliverable" in text:
        entities["request_type"] = "delivery_tracking"
    elif "service request" in text or "complaint" in text:
        entities["request_type"] = "service_request_tracking"
    elif "marketing" in text:
        entities["request_type"] = "marketing_opt_out"

    return {key: value for key, value in entities.items() if value}


def infer_nlu_intent(action: str, entities: dict, text: str) -> str:
    product = entities.get("product", "banking_service")
    feature = entities.get("feature")

    if feature:
        return slug(f"{action}_{feature}")
    if entities.get("fund_house"):
        return slug(f"{action}_{entities['fund_house']}_{product}")
    if entities.get("fund_category"):
        return slug(f"{action}_{entities['fund_category']}_{product}")
    if entities.get("investment_goal"):
        return slug(f"{action}_{entities['investment_goal']}_{product}")
    if entities.get("investment_mode"):
        return slug(f"{action}_{entities['investment_mode']}_{product}")
    if entities.get("biller_type"):
        return slug(f"{action}_{entities['biller_type']}")
    if entities.get("insurance_type"):
        return slug(f"{action}_{entities['insurance_type']}_insurance")
    if entities.get("document_type"):
        return slug(f"{action}_{entities['document_type']}")
    if entities.get("payment_type"):
        return slug(f"{action}_{entities['payment_type']}")
    if entities.get("transaction_status"):
        return slug(f"{action}_{entities['transaction_status']}_{product}_transactions")
    if entities.get("limit_type"):
        return slug(f"{action}_{entities['limit_type']}")
    if entities.get("profile_attribute"):
        return slug(f"{action}_{entities['profile_attribute']}")
    if "balance" in text and action in {"view", "check"}:
        return slug(f"check_{product}_balance")
    if "status" in text and action in {"view", "track"}:
        return slug(f"{action}_{product}_status")
    if action == "view" and ("interest rate" in text or "rate" in text):
        return slug(f"view_{product}_rates")
    if "foreclose" in text:
        return slug(f"foreclose_{product}")

    return slug(f"{action}_{product}")


def build_examples(row: pd.Series) -> str:
    phrases = []
    tags = clean(row.get("tags"))
    if tags:
        phrases.extend(part.strip() for part in tags.split("|") if part.strip())
    phrases.extend([clean(row.get("title")), clean(row.get("label"))])

    seen = set()
    useful = []
    for phrase in phrases:
        normalized = " ".join(phrase.split())
        key = normalized.lower()
        if normalized and key not in seen:
            useful.append(normalized)
            seen.add(key)
        if len(useful) >= 12:
            break
    return "|".join(useful)


def disambiguation_hint(action: str, product: str, entities: dict, row: pd.Series) -> str:
    label = clean(row.get("label")) or clean(row.get("title")) or clean(row.get("intent"))
    parts = [f"Use for {label}."]

    card_type = entities.get("card_type")
    if entities.get("feature"):
        parts.append(f"Feature is {entities['feature'].replace('_', ' ')}.")
    if entities.get("service_type"):
        parts.append(f"Service type is {entities['service_type'].replace('_', ' ')}.")
    if entities.get("biller_type"):
        parts.append(f"Biller type is {entities['biller_type'].replace('_', ' ')}.")
    if entities.get("investment_goal"):
        parts.append(f"Investment goal is {entities['investment_goal'].replace('_', ' ')}.")
    if entities.get("investment_mode"):
        parts.append(f"Investment mode is {entities['investment_mode'].replace('_', ' ')}.")
    if entities.get("insurance_type"):
        parts.append(f"Insurance type is {entities['insurance_type'].replace('_', ' ')}.")
    if card_type:
        parts.append(f"Card type is {card_type.replace('_', ' ')}.")
    if entities.get("status"):
        parts.append(f"Block/status qualifier is {entities['status'].replace('_', ' ')}.")
    if entities.get("transaction_status"):
        parts.append(f"Transaction bucket is {entities['transaction_status']}.")
    if entities.get("deposit_type"):
        parts.append(f"Deposit type is {entities['deposit_type'].replace('_', ' ')}.")
    if entities.get("loan_type"):
        parts.append(f"Loan type is {entities['loan_type'].replace('_', ' ')}.")
    if entities.get("document_type"):
        parts.append(f"Document requested is {entities['document_type'].replace('_', ' ')}.")
    if entities.get("payment_type"):
        parts.append(f"Payment rail or bill type is {entities['payment_type'].replace('_', ' ')}.")
    if entities.get("fund_house"):
        parts.append(f"Fund house is {entities['fund_house'].replace('_', ' ')}.")
    if entities.get("fund_category"):
        parts.append(f"Fund category is {entities['fund_category'].replace('_', ' ')}.")
    if len(parts) == 1:
        parts.append(f"Distinguish by action '{action}' on product '{product.replace('_', ' ')}'.")

    return " ".join(parts)


def apply_row_override(row: pd.Series, nlu_intent: str, entities: dict) -> tuple[str, dict]:
    intent = clean(row.get("intent")).upper()
    override = ROW_OVERRIDES.get(intent)
    if not override:
        return nlu_intent, entities

    overridden_entities = dict(override["entities"])
    return override["nlu_intent"], overridden_entities


def enrich_row(row: pd.Series) -> dict:
    intent = clean(row.get("intent")).upper()
    combined_text = text_for(row)
    primary_text = field_text(row, "intent", "title", "label")
    action = infer_action(intent, combined_text)
    product = infer_product(primary_text)
    if product == "banking_service":
        product = infer_product(combined_text)
    if action == "invest" and ("fund" in primary_text or intent.endswith("_MF")):
        product = "mutual_fund"
    feature = infer_feature(row, product)
    entities = infer_entities(row, action, product, feature, combined_text)
    nlu_intent = infer_nlu_intent(action, entities, primary_text)
    nlu_intent, entities = apply_row_override(row, nlu_intent, entities)
    action = entities.get("action", action)
    product = entities.get("product", product)

    return {
        "nlu_intent": nlu_intent,
        "nlu_entities": json.dumps(entities, sort_keys=True, ensure_ascii=False),
        "nlu_examples": build_examples(row),
        "nlu_disambiguation_hint": disambiguation_hint(action, product, entities, row),
    }


def allowed_duplicate_group(intent_values: set[str]) -> bool:
    return any(intent_values and intent_values.issubset(group) for group in ALLOWED_DUPLICATE_INTENT_GROUPS)


def apply_alias_intents(output_df: pd.DataFrame) -> None:
    alias_intents = {
        "ADD_PAYEE": "add_payee",
        "ADD_BENEFICIARY": "add_payee",
        "VIEW_PAYEE": "view_payee",
        "VIEW_BENEFICIARY": "view_payee",
    }
    for row_index, row in output_df.iterrows():
        intent = clean(row.get("intent")).upper()
        if intent in alias_intents:
            output_df.at[row_index, "nlu_intent"] = alias_intents[intent]


def discriminator_candidates(row: pd.Series) -> list[str]:
    entities = json.loads(row["nlu_entities"])
    candidates = [
        entities.get("feature"),
        entities.get("fund_house"),
        entities.get("fund_category"),
        entities.get("investment_goal"),
        entities.get("investment_mode"),
        entities.get("biller_type"),
        entities.get("insurance_type"),
        entities.get("service_type"),
        entities.get("document_type"),
        entities.get("payment_type"),
        entities.get("loan_type"),
        entities.get("account_type"),
        entities.get("deposit_type"),
        entities.get("transaction_status"),
        entities.get("status"),
        entities.get("limit_type"),
        entities.get("benefit_type"),
        entities.get("card_type"),
        primary_subject(row),
        clean(row.get("intent")),
    ]
    unique = []
    seen = set()
    for candidate in candidates:
        candidate_slug = slug(str(candidate)) if candidate else ""
        if candidate_slug and candidate_slug not in seen:
            unique.append(candidate_slug)
            seen.add(candidate_slug)
    return unique


def resolve_duplicate_nlu_intents(output_df: pd.DataFrame) -> None:
    apply_alias_intents(output_df)

    for _ in range(4):
        changed = False
        duplicate_intents = output_df["nlu_intent"].value_counts()
        duplicate_intents = duplicate_intents[duplicate_intents > 1].index.tolist()

        for nlu_intent in duplicate_intents:
            group = output_df[output_df["nlu_intent"] == nlu_intent]
            original_intents = {clean(value).upper() for value in group["intent"]}
            if allowed_duplicate_group(original_intents):
                continue

            proposed = {}
            used = set()
            for row_index, row in group.iterrows():
                base = clean(row["nlu_intent"])
                for candidate in discriminator_candidates(row):
                    if candidate in base:
                        new_intent = base
                    else:
                        new_intent = slug(f"{base}_{candidate}")
                    if new_intent not in used:
                        break
                else:
                    new_intent = slug(f"{base}_{row_index + 1}")

                proposed[row_index] = new_intent
                used.add(new_intent)

            if len(set(proposed.values())) != len(proposed):
                for row_index, row in group.iterrows():
                    proposed[row_index] = slug(f"{row['nlu_intent']}_{clean(row.get('intent'))}")

            for row_index, new_intent in proposed.items():
                if output_df.at[row_index, "nlu_intent"] != new_intent:
                    output_df.at[row_index, "nlu_intent"] = new_intent
                    changed = True

        if not changed:
            break


def validate(source_df: pd.DataFrame, output_df: pd.DataFrame) -> None:
    if len(source_df) != len(output_df):
        raise ValueError(f"Row count mismatch: source={len(source_df)} output={len(output_df)}")

    missing_source_cols = [column for column in source_df.columns if column not in output_df.columns]
    if missing_source_cols:
        raise ValueError(f"Missing source columns: {missing_source_cols}")

    appended = list(output_df.columns[len(source_df.columns) :])
    if appended != NLU_COLUMNS:
        raise ValueError(f"Unexpected appended columns: {appended}")

    for column in ["nlu_intent", "nlu_entities", "nlu_disambiguation_hint"]:
        empty_count = output_df[column].fillna("").astype(str).str.strip().eq("").sum()
        if empty_count:
            raise ValueError(f"{column} has {empty_count} empty values")

    for index, value in output_df["nlu_entities"].items():
        parsed = json.loads(value)
        if not isinstance(parsed, dict) or not parsed:
            raise ValueError(f"nlu_entities at row {index + 1} is not a non-empty JSON object")

    duplicate_intents = output_df["nlu_intent"].value_counts()
    duplicate_intents = duplicate_intents[duplicate_intents > 1].index.tolist()
    disallowed_duplicates = []
    for nlu_intent in duplicate_intents:
        group = output_df[output_df["nlu_intent"] == nlu_intent]
        original_intents = {clean(value).upper() for value in group["intent"]}
        if not allowed_duplicate_group(original_intents):
            disallowed_duplicates.append((nlu_intent, sorted(original_intents)))
    if disallowed_duplicates:
        raise ValueError(f"Disallowed duplicate nlu_intent groups: {disallowed_duplicates[:10]}")

    expected_rows = {
        "EMAIL_CHANGE": {"nlu_intent": "update_email", "action": "update"},
        "VIEW_INSTANT_SERVICES": {"not_product": "cheque_book"},
        "CC_SETTLEMENT": {"action": "settle"},
        "PAY_BILL": {"product": "bill_payment"},
        "VIEW_UPDATE_PAN": {"nlu_intent": "update_pan_details", "not_action": "view"},
        "ME2ME_TRANSFER": {"action": "transfer"},
    }
    for intent, expectations in expected_rows.items():
        matches = output_df[output_df["intent"].astype(str).str.upper() == intent]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one row for {intent}, found {len(matches)}")

        row = matches.iloc[0]
        entities = json.loads(row["nlu_entities"])
        if expectations.get("nlu_intent") and row["nlu_intent"] != expectations["nlu_intent"]:
            raise ValueError(f"{intent} nlu_intent mismatch: {row['nlu_intent']}")
        if expectations.get("action") and entities.get("action") != expectations["action"]:
            raise ValueError(f"{intent} action mismatch: {entities.get('action')}")
        if expectations.get("not_action") and entities.get("action") == expectations["not_action"]:
            raise ValueError(f"{intent} action should not be {expectations['not_action']}")
        if expectations.get("product") and entities.get("product") != expectations["product"]:
            raise ValueError(f"{intent} product mismatch: {entities.get('product')}")
        if expectations.get("not_product") and entities.get("product") == expectations["not_product"]:
            raise ValueError(f"{intent} product should not be {expectations['not_product']}")



def main() -> None:
    source_df = pd.read_csv(SOURCE)
    enriched = source_df.apply(enrich_row, axis=1, result_type="expand")
    output_df = pd.concat([source_df, enriched[NLU_COLUMNS]], axis=1)
    resolve_duplicate_nlu_intents(output_df)

    validate(source_df, output_df)
    output_df.to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(output_df)} rows and {len(output_df.columns)} columns")


if __name__ == "__main__":
    main()
