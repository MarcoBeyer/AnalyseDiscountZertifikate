import requests

url = "https://api.boerse-frankfurt.de/search/derivative_search"

payload = "{\"types\":[1200],\"subTypes\":[\"10001\"],\"underlyings\":[\"290\"],\"issuers\":null,\"topics\":[],\"units\":null,\"origins\":[],\"participations\":[],\"isPremiumSegment\":null,\"isOpenEnd\":null,\"isQuanto\":null,\"isStopLevel\":null,\"barrierMin\":null,\"barrierMax\":null,\"isBarrierReached\":null,\"bonusLevelMin\":null,\"bonusLevelMax\":null,\"isKnockedOut\":null,\"underlyingFreeField\":null,\"capitalGuaranteeRelMin\":null,\"capitalGuaranteeRelMax\":null,\"strikeMin\":null,\"strikeMax\":null,\"omegaMin\":null,\"omegaMax\":null,\"upperBarrierMin\":null,\"upperBarrierMax\":null,\"rangeLowerMin\":null,\"rangeLowerMax\":null,\"rangeUpperMin\":null,\"rangeUpperMax\":null,\"evaluationDayMin\":null,\"evaluationDayMax\":null,\"tradingTimeStart\":null,\"tradingTimeEnd\":null,\"lang\":\"de\",\"offset\":0,\"limit\":19000,\"sortOrder\":\"DESC\",\"sorting\":\"WKN\"}"
headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Origin': "https://www.boerse-frankfurt.de",
    'cache-control': "no-cache",
    'Postman-Token': "4affd830-60d4-44df-968a-7ec4aefff1ac"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)