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
        res = requests.get("https://api.music.apple.com/v1/catalog/CA/search", {"types":",".join(["songs"]), "term": songInfo["songName"] + " " + songInfo["artists"][0]}, headers=createMutAuth(self._devBearer, mutToken))
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

    def createPlaylist(self, mutToken, title, description, songIds):
        songIdsFormatted = [{"id":id, "type":"songs"} for id in songIds]
        playlistJson = {
            "attributes":{
                "name":title,
                "description":description
            },
            "relationships": {
                "tracks":{
                    "data": songIdsFormatted
                }
            }
        }

        res = requests.post("https://api.music.apple.com/v1/me/library/playlists", json=playlistJson, headers=createMutAuth(self._devBearer, mutToken))

    def createPlaylistFromCommonFormat(self, mutToken, title, description, commonFormat):
        if len(commonFormat) > 0:
            if "appleSongId" in commonFormat[0]:
                self.createPlaylist(mutToken, title, description, [song["appleSongId"] for song in commonFormat])
            else:
                songIds = []
                for song in commonFormat:
                    songId = self.searchSong(mutToken, song)
                    if songId != None:
                        songIds.append(songId)
                    else:
                        print("Search could not find song: " + str(song), flush=True)

                self.createPlaylist(mutToken, title, description, songIds)

    def getPlaylists(self, mutToken):
        result = requests.get("https://api.music.apple.com/v1/me/library/playlists", headers=createMutAuth(self._devBearer, mutToken))
        data = result.json()
        return data
    
    def getPlaylistTracks(self, mutToken, playlistID):
        result = requests.get(f"https://api.music.apple.com/v1/me/library/playlists/{playlistID}/tracks", headers=createMutAuth(self._devBearer, mutToken))
        extendedResult = result.json()
        while "next" in result.json():
            result = requests.get(f"https://api.music.apple.com" + result.json()["next"], headers=createMutAuth(self._devBearer, mutToken))
            extendedResult["data"].extend(result.json()["data"])
        return extendedResult
