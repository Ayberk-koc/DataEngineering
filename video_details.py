import requests
import json
import os
import time
from utils import makeGeneralCall  #hier passiert das ganze callen!

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

APIKEY = os.getenv("APIKEY")

CHANNEL = "MrBeast"


### alter weg:

# #immer mit try catch bei requetsts arbeiten!
# def getPlaylistID():
#     queryParams = {
#         "key": APIKEY,   #hier gibt man key einfach als query-param mit. das ist eig unüblich
#         "forHandle": "MrBeast",
#         "part": "contentDetails"
#     }
#     headers = {    #eigentlich typisch, dass man key so mitgibt und nicht einfach in den query-params
#         "X-API-Key": APIKEY
#     }


#     url = "https://www.googleapis.com/youtube/v3/channels"

#     try:
#         response = requests.get(url, params=queryParams)
#         response.raise_for_status()

#         data = response.json()

#         # with open("data.json", "w") as file:
#         #     json.dump(data, file, indent=4)

#         playlistID = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

#         print(playlistID)

#         return playlistID

#     except requests.exceptions.RequestException as e:
#         raise e

# def getVideoData(maxCount, playlistID, pageToken = None):
#     url = "https://www.googleapis.com/youtube/v3/playlistItems"

#     queryParams = {
#         "maxResults": maxCount,
#         "part": "contentDetails",
#         "key": APIKEY,
#         "playlistId": playlistID,
#         "pageToken": pageToken
#     }

#     payload = {}
#     headers = {}

#     try:
#         response = requests.request("GET", url, params=queryParams ,headers=headers, data=payload)
#         response.raise_for_status()

#         data = response.json()


#         # with open("videos-data.json", "w") as file:
#         #     json.dump(data, file, indent=4)

#         # print(data)
#         return data

#     except requests.exceptions.RequestException as e:
#         raise e

# def getViodeoIDs(playListID):
#     videoIDs = []

#     try:
#         data = getVideoData(50, playListID)

#         while True: 
#             for item in data.get("items", []):
#                 details = item["contentDetails"]
#                 videoID = details["videoId"]
#                 videoIDs.append(videoID)

#             nextPageToken = data.get("nextPageToken", None)

#             if nextPageToken:
#                 data = getVideoData(50, playListID, pageToken=nextPageToken)
#             else:
#                 break

#         print(len(videoIDs))
#         return videoIDs
#     except requests.exceptions.RequestException as e:
#         raise e






def getPlayListIDGeneral(url):
    queryParams = {
        "key": APIKEY,   #hier gibt man key einfach als query-param mit. das ist eig unüblich
        "forHandle": "MrBeast",
        "part": "contentDetails"
    }
    data = makeGeneralCall(url, queryParams=queryParams)   #wie gesagt: Trick ist, so zu tun alb ob die funktion das Problem bereits löst!
    playlistID = data[0]["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    return playlistID


def getRawVideoDataGeneral(url, playListID):
    queryParams = {
        "maxResults": 50,
        "part": "contentDetails",
        "key": APIKEY,
        "playlistId": playListID,
    }

    data = makeGeneralCall(url, queryParams=queryParams) #hier bekomme verschiedene seiten, deswegen ist der return eine liste.

    videoIDs = []
    for pageData in data:
        for item in pageData.get("items", []):
            videoID = item["contentDetails"]["videoId"]
            videoIDs.append(videoID)

    return videoIDs


def batchUpVideoIDs(videoIDs, batchSize=50):
    i = 0
    batchedUpVideoIDs = []
    while i < len(videoIDs):
        upperEnd = i+batchSize if i+batchSize < len(videoIDs) else len(videoIDs)

        videoIDsString = ",".join(videoIDs[i:upperEnd])
        batchedUpVideoIDs.append(videoIDsString)
        i += batchSize

    return batchedUpVideoIDs


def getVideoStatistics(url, videoIDs):
    videosIDsStringList = batchUpVideoIDs(videoIDs)

    totalDataPages = []

    for videoIDsString in videosIDsStringList:
        queryParams = {
            "part": ["statistics", "contentDetails", "snippet"],
            "key": APIKEY,
            "maxResults": 50,
            "id": videoIDsString
        }
        data = makeGeneralCall(url=url, queryParams=queryParams)    #das ist ja wieder eine liste mit mehreren pages!
        for dataPages in data:
            totalDataPages.append(dataPages)

    videoDataList = []
    for totalDataPage in totalDataPages:
        items = totalDataPage.get("items", [])
        for item in items:
            videoId = item.get("id", None)
            snippet = item.get("snippet", {})
            contentDetails = item.get("contentDetails", {})
            statistics = item.get("statistics", {})

            videoData = {
                "videoID": videoId,
                "title": snippet.get("title"),
                "publishedAt": snippet.get("publishedAt"),
                "duration": contentDetails.get("duration"),
                "viewCouunt": statistics.get("viewCount", None),
                "likeCount": statistics.get("likeCount", None),
                "commentCount": statistics.get("commentCount", None)
            }

            videoDataList.append(videoData)

    return videoDataList

    
def saveToJson(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    playListID = getPlayListIDGeneral(url = "https://www.googleapis.com/youtube/v3/channels")
    videoIDs = getRawVideoDataGeneral(url = "https://www.googleapis.com/youtube/v3/playlistItems", playListID=playListID)
    videoStatistics = getVideoStatistics(url="https://youtube.googleapis.com/youtube/v3/videos", videoIDs=videoIDs)
    saveToJson(videoStatistics)







