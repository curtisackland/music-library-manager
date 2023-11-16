import json
import requests
import datetime

SECRETS_FILE = "secrets/keys.json"
BEARER_CACHE_FILE = "secrets/bearer.json"

def interperateSpotifyDateTime(time:str) -> datetime:
    return datetime.datetime.strptime(str(time), "%a, %d %b %Y %H:%M:%S %Z")

def getAPIConfig(keyfile):
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

        with open(BEARER_CACHE_FILE, "w") as bf:
            json.dump(bearerJSON, bf)

    return bearerJSON

class SpotifyAPI:
    def __init__(self) -> None:
        self._apiConfig = getAPIConfig(SECRETS_FILE)
        self._bearerObject = loadBearerToken()
    
    def _getBearerToken(self):
        if datetime.datetime.fromtimestamp(self._bearerObject["expire_time"]) < datetime.datetime.now():
            self._bearerObject = loadBearerToken()

        return self._bearerObject["data"]["access_token"]
            

    def getPlaylists(self, user_id):
        headers={"Authorization":f"Bearer {self._getBearerToken()}"}
        response = requests.get(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers)

        return response.json()

    def getPlaylist(self, playlist_id):
        headers={"Authorization":f"Bearer {self._getBearerToken()}"}
        response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)

        return response.json()
