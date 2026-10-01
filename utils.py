import requests
import time

def __tryMakeCalls(url, method, queryParams, bodyParams, headerParams):
    maxTrials = 3
    for trial in range(maxTrials):
        try:
            response = requests.request(method, url, timeout=10, params=queryParams, json=bodyParams, headers=headerParams)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e: #sollte nur bestimmte errors zum weiterführen bringen.
            if trial == maxTrials-1:
                raise

            status = e.response.status_code if e.response is not None else None

            if status == 429:
                time.sleep(10)
                continue
            elif status is not None and 400 <= status < 500:
                raise
            else:
                time.sleep(2 ** trial)

def makeGeneralCall(url, method="GET", queryParams = None, bodyParams = None, headerParams = None):
    dataToGather = []

    queryParams = dict(queryParams or {})

    while True:
        data = __tryMakeCalls(url, method, queryParams, bodyParams, headerParams)
        dataToGather.append(data)
        
        nextPageToken = data.get("nextPageToken", None)

        if not nextPageToken:
            break

        queryParams["pageToken"] = nextPageToken

    return dataToGather


