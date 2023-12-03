import requests
import jwt
import json
import datetime
import os

def getBearerToken() -> str:
    if os.environ.get("APPLE_BEARER") != None:
        return os.environ.get("APPLE_BEARER")
    else:
        raise Exception("Could not find apple bearer in environment.")


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

