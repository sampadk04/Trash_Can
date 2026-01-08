from vocode.streaming.action.user_authenticated import CustomerAuthenticatedVocodeActionConfig

from vocode.streaming.action.terminate_call import TerminateCallVocodeActionConfig

from vocode.streaming.action.ptp_date_validation import ValidatePTPDateVocodeActionConfig

from vocode.streaming.action.send_payment_link import SendPaymentLinkVocodeActionConfig

from vocode.streaming.action.send_deep_payment_link import SendDeepPaymentLinkVocodeActionConfig

from vocode.streaming.action.guide_oncall_payment import GuideOncallPaymentVocodeActionConfig

from vocode.streaming.action.set_emi_offer import SetEmiOfferVocodeActionConfig

from vocode.streaming.action.ocop_payment_validation import CheckPaymentStatusVocodeActionConfig

from datetime import datetime, timezone, timedelta

from zoneinfo import ZoneInfo
 
 
def get_negotiation_prompt_file(escalation_flag, total_vs_emi_flag):

    if escalation_flag:

        if total_vs_emi_flag == "True":

            system_prompt_dict = {

                "hi": {

                    "female": "prompts/TS1ReleaseCollections/prompt_negotiate_ptp_hi_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_negotiate_escalatory_emi_hi_male.txt"

                }

            }

        else:

            system_prompt_dict = {

                "hi": {

                    "female": "prompts/TS1ReleaseCollections/prompt_negotiate_ptp_hi_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_negotiate_escalatory_total_hi_male.txt"

                }

            }

    else:

        if total_vs_emi_flag == "True":

            system_prompt_dict = {

                "hi": {

                    "female": "prompts/TS1ReleaseCollections/prompt_negotiate_normal_emi_hi_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_negotiate_hi_male.txt"

                }

            }

        else:

            system_prompt_dict = {

                "hi": {

                    "female": "prompts/TS1ReleaseCollections/prompt_negotiate_normal_total_hi_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_negotiate_hi_male.txt"

                }

            }
 
    return system_prompt_dict
 
def get_opening(escalation_flag):

    if escalation_flag:

        initial_message_mapping = {

            "hi": {

                "female": "Hello क्या मेरी बात {customer_name_hinglish} जी से हो रही है? मैं IDFC FIRST Bank head office से senior officer {bot_name} बात कर रही हूँ।",

                "male":   "Hello क्या मेरी बात {customer_name_hinglish} जी से हो रही है? मैं IDFC FIRST Bank head office से senior officer {bot_name} बात कर रहा हूँ।"

            },

            "en": {

                "female": "Hello! Am I speaking to {customer_name_english}? I am a senior officer calling from IDFC FIRST Bank Head Office.",

                "male":   "Hello! Am I speaking to {customer_name_english}? I am a senior officer calling from IDFC FIRST Bank Head Office."

            }

        }

    else:

        initial_message_mapping = {

            "hi": {

                "female": "{greeting} मैं IDFC First Bank से {bot_name} बोल रही हूँ। क्या मेरी बात {customer_name_hinglish} जी से हो रही है?",

                "male":   "{greeting} मैं IDFC First Bank से {bot_name} बोल रहा हूँ। क्या मेरी बात {customer_name_hinglish} जी से हो रही है?",

            },

            "en": {

                "female": "{greeting} I am {bot_name} calling from IDFC First Bank. Am I speaking to {customer_name_english}?",

                "male":   "{greeting} I am {bot_name} calling from IDFC First Bank. Am I speaking to {customer_name_english}?",

            },

        }

    return initial_message_mapping
 
def get_negotiate_actions(total_vs_emi_flag):

    """

    Returns the appropriate actions for the negotiate node based on total_vs_emi_flag.

    When total_vs_emi_flag is True (EMI case), SetEmiOfferVocodeActionConfig is excluded.

    """

    actions = [

        GuideOncallPaymentVocodeActionConfig(), 

        ValidatePTPDateVocodeActionConfig(), 

        SendPaymentLinkVocodeActionConfig(), 

        SendDeepPaymentLinkVocodeActionConfig(),

        TerminateCallVocodeActionConfig()

    ]

    # Only add SetEmiOfferVocodeActionConfig when total_vs_emi_flag is False (total payment case)

    if total_vs_emi_flag != "True":

        actions.append(SetEmiOfferVocodeActionConfig())

    return actions
 
def setup_nodes(escalation_flag, total_vs_emi_flag):

    NODES = [

        {

            "nodeId": 1,

            "nodeName": "authenticate",

            "nodeDescription": "Authenticates the customer",

            "systemPromptFile": {

                "hi": {

                    "female": "prompts/TS1ReleaseCollections/prompt_authenticate_hi_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_authenticate_hi_male.txt"

                },

                "en": {

                    "female": "prompts/TS1ReleaseCollections/prompt_authenticate_en_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_authenticate_en_male.txt"

                }

            },

            "onEndTransferToNode": 2,

            "requiresSummaryFromPrevNode": False,

            "requiresSessionConversation": False,

            "initialMessage" : get_opening(escalation_flag),

            "actions": [CustomerAuthenticatedVocodeActionConfig(), TerminateCallVocodeActionConfig()]

        },

        {

            "nodeId": 2,

            "nodeName": "negotiate",

            "nodeDescription": "Negotiates with the customer to collect the payment",

            "systemPromptFile": get_negotiation_prompt_file(escalation_flag, total_vs_emi_flag),

            "onEndTransferToNode": 3,

            "requiresSummaryFromPrevNode": False,

            "requiresSessionConversation": True,

            "initialMessage": {},

            "actions": get_negotiate_actions(total_vs_emi_flag)

        },

        {

            "nodeId": 3,

            "nodeName": "oncall_payment",

            "nodeDescription": "This node helps with guiding the user with the payment process over the call.",

            "systemPromptFile": {

                "hi": {

                    "female": "prompts/TS1ReleaseCollections/prompt_ocop_hi_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_ocop_hi_male.txt"

                },

                "en": {

                    "female": "prompts/TS1ReleaseCollections/prompt_ocop_en_female.txt",

                    "male": "prompts/TS1ReleaseCollections/prompt_ocop_en_male.txt"

                }

            },

            "onEndTransferToNode": "",

            "requiresSummaryFromPrevNode": False,

            "requiresSessionConversation": False,

            "initialMessage": {

                "hi": {

                    "male": "Please जो secure payment लिंक आपको WhatsApp या SMS पे भेजा गया है, उसे click करें",

                    "female": "Please जो secure payment लिंक आपको WhatsApp या SMS पे भेजा गया है, उसे click करें"},

                "en": {

                    "male": "Please click on the secure payment link sent by the bank over WhatsApp and SMS",

                    "female": "Please click on the secure payment link sent by the bank over WhatsApp and SMS"

                }

            },

            "actions": [SendPaymentLinkVocodeActionConfig(), SendDeepPaymentLinkVocodeActionConfig(), CheckPaymentStatusVocodeActionConfig(), TerminateCallVocodeActionConfig()]

        }    ]
 
    return NODES
 
