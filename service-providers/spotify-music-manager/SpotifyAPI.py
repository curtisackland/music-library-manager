import json
import requests
import os
import datetime
import base64
import math

SECRETS_FILE = "secrets/keys.json"
BEARER_CACHE_FILE = "secrets/bearer.json"

def interperateSpotifyDateTime(time:str) -> datetime:
    return datetime.datetime.strptime(str(time), "%a, %d %b %Y %H:%M:%S %Z")

def getAPIConfig(keyfile):
    if os.environ.get("SPOTIFY_CLIENT_ID") != None and os.environ.get("SPOTIFY_CLIENT_SECRET") != None:
        return {"app":{"client_id":os.environ.get("SPOTIFY_CLIENT_ID"), "client_secret":os.environ.get("SPOTIFY_CLIENT_SECRET")}}
    else:
        raise Exception("Could not find spotify credentials in environment.")


def getNewBearerTokenObject(clientID, clientSecret):
    header = {"Content-Type":"application/x-www-form-urlencoded"}
    params = {"grant_type":"client_credentials", "client_id":clientID, "client_secret":clientSecret}
    response = requests.post("https://accounts.spotify.com/api/token", headers=header, data=params)

    responseTime = response.headers["date"]
    #responseTime = 'Mon, 30 Oct 2023 20:12:44 GMT'


    if not response.ok:
        raise RuntimeError(f"{response.status_code}:{response.text}")

    responseTimeObject = interperateSpotifyDateTime(responseTime)
    return {"data": response.json(), "requestTime":datetime.datetime.timestamp(responseTimeObject), "expire_time":datetime.datetime.timestamp(responseTimeObject + datetime.timedelta(0, response.json()["expires_in"]))}

def loadBearerToken():
    bearerJSON = None
    try:
        with open(BEARER_CACHE_FILE, "r") as bf: # Load existing token
            bearerJSON = json.load(bf)

    except FileNotFoundError:
        pass

    isExpired = False
    if bearerJSON != None:
        if datetime.datetime.fromtimestamp(bearerJSON["expire_time"]) < datetime.datetime.now():
            isExpired = True

    if bearerJSON == None or isExpired:
        cfg = getAPIConfig(SECRETS_FILE)
        bearerJSON = getNewBearerTokenObject(cfg["app"]["client_id"], cfg["app"]["client_secret"])
        if not os.path.exists(os.path.dirname(BEARER_CACHE_FILE)):
            os.mkdir(os.path.dirname(BEARER_CACHE_FILE))
        with open(BEARER_CACHE_FILE, "w") as bf:
            json.dump(bearerJSON, bf)

    return bearerJSON

def createAuth(bearer):
    return {"Authorization":"Bearer " + bearer}


class SpotifyAPI:
    def __init__(self) -> None:
        self._apiConfig = getAPIConfig(SECRETS_FILE)
        self._bearerObject = loadBearerToken()
    
    def _getBearerToken(self):
        if datetime.datetime.fromtimestamp(self._bearerObject["expire_time"]) < datetime.datetime.now():
            self._bearerObject = loadBearerToken()

        return self._bearerObject["data"]["access_token"]

    def _getBasicAuth(self) -> str:
        return base64.b64encode(bytes((self._apiConfig["app"]["client_id"] + ":" + self._apiConfig["app"]["client_secret"]), "utf-8")).decode("utf-8")

    def getUserName(self, userToken:str) -> str:
        ret = requests.get("https://api.spotify.com/v1/me", headers=createAuth(userToken))
        return ret.json()["id"]
    
    def createPlaylist(self, userToken:str, playlistName:str, playlistDescription:str, public:str, tracks:list) -> str:
        newPlaylistBody = {
          "name": playlistName,
          "description": playlistDescription,
          "public": public,
        }

        newPlaylist = requests.post(f"https://api.spotify.com/v1/users/{requests.utils.quote(self.getUserName(userToken))}/playlists", json=newPlaylistBody, headers=createAuth(userToken))

        trackGroups = []

        for groupNum in range(math.ceil(len(tracks)/100)):
            group = []
            offset = groupNum * 100
            for songNum in range(min(len(tracks[offset:]), 100)):
                group.append(tracks[songNum + offset])
            trackGroups.append(group)

        for trackGroupNumber in range(len(trackGroups)):
            addTracksBody = {
                "uris":trackGroups[trackGroupNumber]
            }
            newPlaylistId = newPlaylist.json()["id"]
            requests.post(f"https://api.spotify.com/v1/playlists/{requests.utils.quote(newPlaylistId)}/tracks", json=addTracksBody, headers=createAuth(userToken))

    def getUserAuthenticationToken(self, code:str, redirect_uri:str) -> requests.Response:

        headers = {
            "Authorization":f"Basic {self._getBasicAuth()}",
            "content-type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri # Redirect URI here is just for verification
        }
        ret = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        return ret

    def getPlaylists(self, userToken:str):
        response = requests.get(f"https://api.spotify.com/v1/users/{requests.utils.quote(self.getUserName(userToken))}/playlists", headers=createAuth(userToken))
        return response.json()

    def getPlaylist(self, userToken:str, playlistId:str):
        response = requests.get(f"https://api.spotify.com/v1/playlists/{playlistId}/tracks", headers=createAuth(userToken))
        extendedPlaylistItems = response.json()
        while "next" in response.json() and response.json()["next"] != None:
            response = requests.get(response.json()["next"], headers=createAuth(userToken))
            extendedPlaylistItems["items"].extend(response.json()["items"])
        
        return extendedPlaylistItems

    def searchSong(self, userToken:str, songInfo:dict):
        attributes = {"songName":"track"}
        listAttributes = {"artists":"artist"}
        songQuery = ""
        for attr in attributes:
            if attr in songInfo:
                songQuery += requests.utils.quote(attributes[attr]) + ":" + requests.utils.quote(songInfo[attr] + " ")

        for attr in listAttributes:
            if attr in songInfo and len(songInfo[attr]) > 0:
                songQuery += requests.utils.quote(listAttributes[attr]) + ":" + requests.utils.quote(songInfo[attr][0] + " ")

        searchParams = {"type":"track","limit":1,"q":requests.utils.quote(songQuery)}
        res = requests.get("https://api.spotify.com/v1/search", searchParams, headers=createAuth(userToken))
        if res.ok:
            resJson = res.json()
            if "tracks" in resJson:
                if "items" in resJson["tracks"]:
                    if len(resJson["tracks"]["items"]) != 0:
                        return resJson["tracks"]["items"][0]["uri"]
        return None

    def getClientID(self):
        return self._apiConfig["app"]["client_id"]
    
    def createPlaylistFromCommonFormat(self, bearer, title, description, public, commonFormat):

        if len(commonFormat) > 0:
            if "spotifySongId" in commonFormat[0]:
                self.createPlaylist(bearer, title, description, public, ["spotify:track:" + song["spotifySongId"] for song in commonFormat])
            else:
                songIds = []
                for song in commonFormat:
                    songId = self.searchSong(bearer, song)
                    if songId != None:
                        songIds.append(songId)
                    else:
                        print("Search could not find song: " + str(song), flush=True)

                self.createPlaylist(bearer, title, description, True, songIds)
