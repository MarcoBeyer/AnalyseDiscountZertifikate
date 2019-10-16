#!/usr/bin/env python3

import json
import time
import requests
import pandas as pd

url = "https://api.boerse-frankfurt.de/search/derivative_search"

payload = '''
{
    "types": [1200],
    "subTypes": ["10001"],
    "underlyings": ["290"],
    "issuers": null,
    "topics": [],
    "units": null,
    "origins": [],
    "participations": [],
    "isPremiumSegment": null,
    "isOpenEnd": null,
    "isQuanto": null,
    "isStopLevel": null,
    "barrierMin": null,
    "barrierMax": null,
    "isBarrierReached": null,
    "bonusLevelMin": null,
    "bonusLevelMax": null,
    "isKnockedOut": null,
    "underlyingFreeField": null,
    "capitalGuaranteeRelMin": null,
    "capitalGuaranteeRelMax": null,
    "strikeMin": null,
    "strikeMax": null,
    "omegaMin": null,
    "omegaMax": null,
    "upperBarrierMin": null,
    "upperBarrierMax": null,
    "rangeLowerMin": null,
    "rangeLowerMax": null,
    "rangeUpperMin": null,
    "rangeUpperMax": null,
    "evaluationDayMin": null,
    "evaluationDayMax": null,
    "tradingTimeStart": null,
    "tradingTimeEnd": null,
    "lang": "de",
    "offset": 0,
    "limit": 1000000,
    "sortOrder": "DESC",
    "sorting": "WKN"
}
'''

headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Origin': "https://www.boerse-frankfurt.de"
}

response = requests.request("POST", url, data=payload, headers=headers)
timestr = time.strftime("%Y_%m_%d-%H_%M")
dataframe = pd.DataFrame(json.loads(response.text)["data"])
dataframe = dataframe.rename(columns = {"isin": "ISIN",
                                        "cap": "Cap", 
                                        "evaluationDay": "Bewertungstag", 
                                        "issuerName": "Emittent", 
                                        "ask": "Brief", 
                                        "bid": "Geld"})[["ISIN", "Cap", "Bewertungstag", "Emittent", "Brief", "Geld"]]
dataframe.to_csv("Discount_Frankfurt_" + timestr + ".csv", index = False)
