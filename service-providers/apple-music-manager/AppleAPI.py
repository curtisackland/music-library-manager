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

    def searchSong(self, mutToken, songInfo):
        res = requests.get("https://api.music.apple.com/v1/catalog/CA/search", {"types":",".join(["songs"]), "term": songInfo["songName"]}, headers=createMutAuth(self._devBearer, mutToken))
        if res.ok:
            with open("tmp.json", "w") as f:
                json.dump(res.json(), f, indent=2)
            resJson = res.json()
            if "results" in resJson:
                if "songs" in resJson['results']:
                    if "data" in resJson['results']['songs']:
                        if len(resJson) != 0:
                            if "id" in resJson['results']['songs']['data'][0]:
                                return resJson['results']['songs']['data'][0]['id']
        return None

    def createPlaylist(self, mutToken, title, descr, songIds):
        songIdsFormatted = [{"id":id, "type":"songs"} for id in songIds]
        playlistJson = {
            "attributes":{
                "name":title,
                "description":descr
            },
            "relationships": {
                "tracks":{
                    "data": songIdsFormatted
                }
            }
        }

        res = requests.post("https://api.music.apple.com/v1/me/library/playlists", json=playlistJson, headers=createMutAuth(self._devBearer, mutToken))

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

