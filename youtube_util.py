from json import loads
from time import sleep

import requests

def getinitialdata(html: str):
    for line in html.splitlines():
        if 'var ytInitialData = ' in line.strip():
            return loads(line.split('var ytInitialData = ', 1)[1].split(";</script><script ", 1)[0])
    return {}

def getapikey(html: str):
    return html.split('"INNERTUBE_API_KEY":"', 1)[-1].split('"', 1)[0]

#extract latest version automatically
def getlver(initialdata: dict):
    try:
        return initialdata["responseContext"]["serviceTrackingParams"][2]["params"][2]["value"]
    except:
        return "2.20220720.00.00"

def fullyexpand(inputdict: dict, mysession: requests.session, params: tuple, API_VERSION: str):
    lastrequestj = inputdict["items"]
    
    while "continuationItemRenderer" in lastrequestj[-1].keys():
        while True:
            data = {"context":{"client":{"hl":"en","gl":"US","clientName":"WEB","clientVersion":API_VERSION}},"continuation": lastrequestj[-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]}
            lastrequest = mysession.post("https://www.youtube.com/youtubei/v1/browse", params=params, json=data)
            if lastrequest.status_code == 200:
                break
            else:
                print("Non-200 API status code, waiting 30 seconds before retrying...")
                sleep(30)
        lastrequestj = lastrequest.json()["onResponseReceivedActions"][0]["appendContinuationItemsAction"]["continuationItems"]
        inputdict["items"].pop()
        inputdict["items"].extend(lastrequestj)

    return inputdict
