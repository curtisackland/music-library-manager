import json
import requests
import os
import datetime
import base64

SECRETS_FILE = "secrets/keys.json"
BEARER_CACHE_FILE = "secrets/bearer.json"

def interperateSpotifyDateTime(time:str) -> datetime:
    return datetime.datetime.strptime(str(time), "%a, %d %b %Y %H:%M:%S %Z")

def getAPIConfig(keyfile):
    if os.environ.get("SPOTIFY_CLIENT_ID") != None and os.environ.get("SPOTIFY_CLIENT_SECRET") != None:
        return {"app":{"client_id":os.environ.get("SPOTIFY_CLIENT_ID"), "client_secret":os.environ.get("SPOTIFY_CLIENT_SECRET")}}
    else:
        print("Could not find spotify credentials in environment. Looking for file...")
        with open(keyfile, "r") as keyfileptr:
            return json.load(keyfileptr)

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

        addTracksBody = {
          "uris":tracks,
          "position":0
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
        return response.json()
    
    def getClientID(self):
        return self._apiConfig["app"]["client_id"]
