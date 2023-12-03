import requests
import jwt
import json
import datetime

CONFIG_FILE = "secrets/config.json"

def getConfig():
    with open(CONFIG_FILE, "r") as inConfigFile:
        return json.load(inConfigFile)

def getPrivateKey() -> str:
        with open(getConfig()["privateKeyFile"], "r") as inKeyFile:
            return inKeyFile.read()

def generateNewDeveloperBearer():
    headers = {
        "kid":getConfig()["kid"]
    }
    iat = datetime.datetime.now().timestamp()
    body = {
        "iss": getConfig()["iss"],
        "iat": iat,
        "exp": iat + 2592000, # 1 month
    }

    privateKey = getPrivateKey()
    bearer = jwt.encode(body, headers=headers, key=privateKey, algorithm="ES256")

    bearerJson = {
        "bearer":bearer,
        "exp":iat + 2592000,
    }

    with open(getConfig()["bearerCache"], "w") as outBearerFile:
        json.dump(bearerJson, outBearerFile)

    return bearerJson

def getBearerToken() -> str:
    try:
        with open(getConfig()["bearerCache"], "r") as inBearerFile:
            j = json.load(inBearerFile)
            return j["bearer"]
    except FileNotFoundError:
        return generateNewDeveloperBearer()["bearer"]

def createDevAuth(devBearer):
    return {"Authorization":"Bearer " + devBearer}

def createMutAuth(devBearer, mutToken):
    return {"Authorization":"Bearer " + devBearer, "Music-User-Token": mutToken}


class AppleAPI:
    def __init__(self):
        self._devBearer = getBearerToken()

    def getPlaylists(self, mutToken):
        result = requests.get("https://api.music.apple.com/v1/me/library/playlists", headers=createMutAuth(self._devBearer, mutToken))
        print(result.text, flush=True)
        data = result.json()
        return data
    
    def getPlaylistTracks(self, mutToken, playlistID):
        result = requests.get(f"https://api.music.apple.com/v1/me/library/playlists/{playlistID}/tracks", headers=createMutAuth(self._devBearer, mutToken))
        print(result.text, flush=True)
        data = result.json()
        return data

