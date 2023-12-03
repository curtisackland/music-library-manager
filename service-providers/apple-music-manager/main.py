import os
import re
import threading
import requests
import time
import flask
from flask_cors import CORS
from typing import List

import AppleAPI

app = flask.Flask(__name__)
CORS(app)

api = AppleAPI.AppleAPI()

TIME_BETWEEN_REQUESTS = 30

SEND_HEARTBEAT = True

def getCommonFormatSongsFromPlaylists(userToken: str, playlistIDs: List[str]):
    songs = []
    for playlistID in playlistIDs:
        playlist = api.getPlaylistTracks(userToken, playlistID)
        for track in playlist["data"]:
            newSong = {}

            newSong["songName"] = track["attributes"]["name"]
            newSong["artist"] = track["attributes"]["artistName"]
            newSong["genres"] = track["attributes"]["genreNames"]
            newSong["album"] = track["attributes"]["albumName"]
            newSong["songLength"] = track["attributes"]["durationInMillis"]
            newSong["releaseDate"] = track["attributes"]["releaseDate"]
            newSong["songId"] = track["id"]

            songs.append(newSong)

    return songs

def getRegistryURL() -> str:
    if re.search("localhost", os.environ.get('REGISTRY_URL')):
        return re.sub("localhost", "host.docker.internal", os.environ.get('REGISTRY_URL'))
    else:
        return os.environ.get('REGISTRY_URL')

def sendHeartbeat() -> None:
    global SEND_HEARTBEAT
    count = TIME_BETWEEN_REQUESTS
    while SEND_HEARTBEAT:
        if count >= TIME_BETWEEN_REQUESTS:
            data = {
                "url": os.environ.get('PROVIDER_URL'),
                "type": "register",
                "name": "Apple Library Manager"
            }
            print("Heartbeat: " + str(requests.post(getRegistryURL() + "/heartbeat", json=data)), flush=True)
            count = 0
        count += 1
        time.sleep(1)


@app.route("/userPlaylists")
def userPlaylists():
    return api.getPlaylists(flask.request.args.get("userToken"))


@app.route('/export')
def exportPlaylist():
    return getCommonFormatSongsFromPlaylists(flask.request.args.get("userToken"), [flask.request.args.get("playlistId")])


@app.route('/import', methods=['POST'])
def importPlaylist():
    # TODO import common format and create a new playlist based of it
    return "Apple import endpoint"


@app.route('/shuffle', methods=['POST'])
def shuffle():
    # TODO implement shuffle
    print(flask.request.json)
    return flask.request.json


@app.route('/sort', methods=['POST'])
def sort():
    # TODO implement sort
    print(flask.request.json)
    return flask.request.json


@app.route("/getDeveloperToken")
def getDeveloperToken():
    return AppleAPI.getBearerToken()


if __name__ == '__main__':
    t1 = threading.Thread(target=sendHeartbeat)
    t1.start()
    app.run(host='0.0.0.0', port=3002)

    # unregisters the service from the registry on stop
    SEND_HEARTBEAT = False
    endRequest = {
        "url": os.environ.get('PROVIDER_URL'),
        "type": "unregister",
        "name": "Apple Library Manager"
    }
    requests.post(getRegistryURL() + "/heartbeat", json=endRequest)
    t1.join()
