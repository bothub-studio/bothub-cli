intent_info = {
        "id": "",
        "name": "",
        "auto": True,
        "contexts": [],
        "responses": [
            {
                "resetContexts": False,
                "action": "",
                "affectedContexts": [],
                "parameters": [],
                "messages": [
                    {
                        "type": 0,
                        "lang": "ko",
                        "speech": []
                    }
                ],
                "defaultResponsePlatforms": {},
                "speech": []
            }
        ],
        "priority": 500000,
        "webhookUsed": False,
        "webhookForSlotFilling": False,
        "fallbackIntent": False,
        "events": []
    }

intent_usersays = {
    "id": "",
    "data": [
        {
            "text": "",
            "userDefined": False
        }
    ],
    "isTemplate": False,
    "count": 0,
    "updated": 0
}

entity_info = {
  "id": "",
  "name": "",
  "isOverridable": True,
  "isEnum": False,
  "automatedExpansion": False
}

entity_entries = [
  {
    "value": "",
    "synonyms": []
  }
]

entity_yaml = {
  "Default_entity": {
    "name": "default",
    "data": [
      {
        "value": "fruit",
        "synonyms": [
          "apple",
          "banana",
          "melon",
          "strawberry",
          "blueberry"
        ]
      }
    ]
  }
}



agent_info = {
    "description": "",
    "language": "ko",
    "disableInteractionLogs": False,
    "disableStackdriverLogs": True,
    "googleAssistant": {
        "googleAssistantCompatible": False,
        "project": "",
        "welcomeIntentSignInRequired": False,
        "startIntents": [],
        "systemIntents": [],
        "endIntentIds": [],
        "oAuthLinking": {
            "required": False,
            "grantType": "AUTH_CODE_GRANT"
        },
        "voiceType": "MALE_1",
        "capabilities": [],
        "protocolVersion": "V2",
        "isDeviceAgent": False
    },
    "defaultTimezone": "Asia/Tokyo",
    "webhook": {
        "available": False,
        "useForDomains": False,
        "cloudFunctionsEnabled": False,
        "cloudFunctionsInitialized": False
    },
    "isPrivate": True,
    "customClassifierMode": "use.after",
    "mlMinConfidence": 0.3,
    "supportedLanguages": [],
    "onePlatformApiVersion": "v2",
    "analyzeQueryTextSentiment": False,
    "enabledKnowledgeBaseNames": [],
    "knowledgeServiceConfidenceAdjustment": -0.4,
    "dialogBuilderMode": False
}

package_info = {
    "version": "1.0.0"
}