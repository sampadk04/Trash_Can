from datetime import datetime
from vocode.streaming.action.plx_calculate import CalculateEMIActionConfig
from vocode.streaming.action.terminate_call import TerminateCallVocodeActionConfig
from vocode.streaming.action.user_authenticated import CustomerAuthenticatedVocodeActionConfig
from vocode.streaming.action.plx_capture_appointment_datetime import CaptureAppointmentDateTimeVocodeActionConfig
from vocode.streaming.action.plxsell_customer_convinced import CustomerConvincedLoanVocodeActionConfig
from vocode.streaming.action.plx_negative_profiles import CaptureNegativeProfileVocodeActionConfig
from vocode.streaming.action.plx_capture_address import ConfirmLocationPreferenceVocodeActionConfig
from vocode.streaming.action.sales_create_warm_and_cold_leads import CreateSalesLeadsActionConfig
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


NODES = [
    {
        "nodeId": 1,
        "nodeName": "authenticate",
        "nodeDescription": "Authenticates the customer",
        "systemPromptFile": {
            "hi": {
                "female": "prompts/PLXSell/prompt_PLXSell_authenticate_hi_female.txt",
                "male":   "prompts/PLXSell/prompt_PLXSell_authenticate_hi_male.txt",
            },
            "en": {
                "female": "prompts/PLXSell/prompt_PLXSell_authenticate_en_female.txt",
                "male":   "prompts/PLXSell/prompt_PLXSell_authenticate_en_male.txt",
            },
        },
        "onEndTransferToNode": 2,
        "requiresSummaryFromPrevNode": False,
        "requiresSessionConversation": False,
        "initialMessage": {
            "hi": {
                "female": "{greeting} मैं IDFC First Bank से {bot_name} बोल रही हूँ। क्या मै {name_hi} जी से बात कर रही हूँ?",
                "male":   "{greeting} मैं IDFC First Bank से Rahul बोल रहा हूँ। क्या मै {name_hi} जी से बात कर रहा हूँ?",
            },
            "en": {
                "female": "{greeting} I am {bot_name} calling from IDFC First Bank. Am I speaking to {name_en}?",
                "male":   "{greeting} I am Rahul calling from IDFC First Bank. Am I speaking to {name_en}?",
            },
        },
        "actions": [
            CustomerAuthenticatedVocodeActionConfig(),
            TerminateCallVocodeActionConfig(),
        ],
        "allowInterruptions": True,
        "enable_delayed_processing": False,
        "min_delay_time": 0,
        "max_delay_time": 0,
        "delay_time_step": 0
    },
    {
        "nodeId": 2,
        "nodeName": "plxsell_converse",
        "nodeDescription": "conduct outbound phone calls to existing customers who are eligible for a pre-approved personal loan.",
        "systemPromptFile": {
            "hi": {
                "female": "prompts/PLXSell/prompt_PLXSellAppointment_converse_hi_female.txt",
                "male":   "prompts/PLXSell/prompt_PLXSellAppointment_converse_hi_male.txt",
            },
            "en": {
                "female": "prompts/PLXSell/prompt_PLXSellAppointment_converse_en_female.txt",
                "male":   "prompts/PLXSell/prompt_PLXSellAppointment_converse_en_male.txt",
            },
        },
        "onEndTransferToNode": 3,
        "requiresSummaryFromPrevNode": False,
        "requiresSessionConversation": False,
        "initialMessage": {},
        "actions": [
            CalculateEMIActionConfig(),
            CustomerConvincedLoanVocodeActionConfig(),
            TerminateCallVocodeActionConfig(),
            CreateSalesLeadsActionConfig(),
        ],
        "allowInterruptions": True,
        "enable_delayed_processing": False,
        "min_delay_time": 0,
        "max_delay_time": 0,
        "delay_time_step": 0
    },
    {
        "nodeId": 3,
        "nodeName": "plxsell_appointment",
        "nodeDescription": "take appointment details from the customer for a bank representative to visit them",
        "systemPromptFile": {
            "hi": {
                "female": "prompts/PLXSell/prompt_PLXSellAppointment_appointment_hi_female.txt",
                "male":   "prompts/PLXSell/prompt_PLXSellAppointment_appointment_hi_male.txt",
            },
            "en": {
                "female": "prompts/PLXSell/prompt_PLXSellAppointment_appointment_en_female.txt",
                "male":   "prompts/PLXSell/prompt_PLXSellAppointment_appointment_en_male.txt",
            },
        },
        "onEndTransferToNode": "",
        "requiresSummaryFromPrevNode": False,
        "requiresSessionConversation": False,
        "initialMessage": {},
        "actions": [
            TerminateCallVocodeActionConfig(),
            CaptureAppointmentDateTimeVocodeActionConfig(),
            CaptureNegativeProfileVocodeActionConfig(),
            ConfirmLocationPreferenceVocodeActionConfig()
        ],
        "allowInterruptions": False,
        "enable_delayed_processing": False,
        "min_delay_time": 1,
        "max_delay_time": 3,
        "delay_time_step": 0.5
    }
]
