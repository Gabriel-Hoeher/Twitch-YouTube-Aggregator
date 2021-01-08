from social_scraper.celery import app
from googleapiclient.discovery import build
from time import sleep
import requests

from .models import Media, CreatorInfo, CreatorLiveStatus
from .secrets import clientID, secret, ytAPIKey

TwitchURL = 'https://api.twitch.tv/helix/streams?user_login='
authURL = 'https://id.twitch.tv/oauth2/token'
AutParams = { 'client_id': clientID, 'client_secret': secret, 'grant_type': 'client_credentials' }

@app.task
def createVideos(creatorInfo):
    content = youtube.channels().list(id=creatorInfo.youtubeID, part='contentDetails').execute()
    playlistId = content['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    vids = youtube.playlistItems().list(playlistId=playlistId, part='snippet', maxResults=5, pageToken=None).execute()['items']

    for i,vid in enumerate(reversed(vids)):
        title = vid['snippet']['title']
        date = vid['snippet']['publishedAt'].split('T')[0]
        link = vid['snippet']['resourceId']['videoId']

        totalVids = len(vids)
        Media.objects.create(
            creatorName = youtube.channels().list(id=creatorInfo.youtubeID, part='snippet').execute()['items'][0]['snippet']['title'],
            creatorID = creatorInfo,
            data = {
                'platform': 'YouTube',
                'contentData': {
                    'title': title, 
                    'link': 'https://www.youtube.com/watch?v='+link,
                    'date': date, 
                    'rank': totalVids - i
                }
            })
    sleep(3)

@app.task
def updateVideos(channelID, creatorID):
    content = youtube.channels().list(id=channelID, part='contentDetails').execute()
    playlistId = content['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    vids = youtube.playlistItems().list(playlistId=playlistId, part='snippet', maxResults=5, pageToken=None).execute()['items']
    totalVids = len(vids)

    for i,vid in reversed(enumerate(vids)):
        title = vid['snippet']['title']
        date = vid['snippet']['publishedAt']
        link = vid['snippet']['resourceId']['videoId']
        
        obj = Media.objects.filter(creatorID=creatorID, data__platform ='YouTube', data__contentData__rank = (totalVids-i)).first()
        obj.data['contentData']['title'] = title
        obj.data['contentData']['link'] = 'https://www.youtube.com/watch?v='+link
        obj.data['contentData']['date'] = date
        obj.save()

    sleep(3)

@app.task(name='connectAndCreate')
def connectAndCreate(urlID):
    createVideos(CreatorInfo.objects.get(youtubeID=urlID))

@app.task(name='updateLive')
def updateAllLiveStatus():
    for status in CreatorLiveStatus.objects.all():
        status.isLiveTwitch = isOnlineTwitch(status.creatorID.twitchName)
        status.isLiveYoutube = isLiveYoutube(status.creatorID.youtubeID)

@app.task(name='updateAllVideos')
def updateAllVideos():
    for creator in CreatorInfo.objects.all():
        updateVideos(creator.youtubeID, creator.ID)


#connect to twitch
def isOnlineTwitch(username):
    if username == "": return False
    AutCall = requests.post(url=authURL, params=AutParams) 
    accessToken = AutCall.json()['access_token']

    head = { 'Client-ID': clientID, 'Authorization': "Bearer " + accessToken }
    r = requests.get(TwitchURL+username, headers = head).json()['data']

    if r:
        if r[0]['type'] == 'live': return True
    else: return False

def isOnlineYT(ytID):
    if ytID == "": return False 
    head = {'channelId': ytID, 'eventType': 'live', 'type': 'video', 'key': ytAPIKey}
    r = requests.get('https://youtube.googleapis.com/youtube/v3/search?', params=head).json()
    if not r['items']: return False              #checks if items is empty
    else: return True

#create key and connect to v3
def connectToYouTube(): 
    global youtube 
    youtube = build('youtube', 'v3', developerKey=ytAPIKey)

connectToYouTube()