import json
from datetime import date
from api.utils import makeGeneralCall

from airflow.decorators import task
from airflow.models import Variable


API_KEY = Variable.get("API_KEY")
CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")

@task
def getPlayListIDGeneral(url):
    queryParams = {
        "key": API_KEY,   #hier gibt man key einfach als query-param mit. das ist eig unüblich
        "forHandle": CHANNEL_HANDLE,
        "part": "contentDetails"
    }
    data = makeGeneralCall(url, queryParams=queryParams)   #wie gesagt: Trick ist, so zu tun alb ob die funktion das Problem bereits löst!
    playlistID = data[0]["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    return playlistID

@task
def getRawVideoDataGeneral(url, playListID):
    queryParams = {
        "maxResults": 50,
        "part": "contentDetails",
        "key": API_KEY,
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

@task
def getVideoStatistics(url, videoIDs):
    videosIDsStringList = batchUpVideoIDs(videoIDs)

    totalDataPages = []

    for videoIDsString in videosIDsStringList:
        queryParams = {
            "part": ["statistics", "contentDetails", "snippet"],
            "key": API_KEY,
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

@task
def saveToJson(data):
    with open(f"./data/YT_data_{date.today()}.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    playListID = getPlayListIDGeneral(url = "https://www.googleapis.com/youtube/v3/channels")
    videoIDs = getRawVideoDataGeneral(url = "https://www.googleapis.com/youtube/v3/playlistItems", playListID=playListID)
    videoStatistics = getVideoStatistics(url="https://youtube.googleapis.com/youtube/v3/videos", videoIDs=videoIDs)
    saveToJson(videoStatistics)







