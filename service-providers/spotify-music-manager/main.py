import os
import sys
import threading
import requests
import time
import flask
import re
from flask_cors import CORS
import SpotifyAPI

app = flask.Flask(__name__)
CORS(app)

api = SpotifyAPI.SpotifyAPI()

TIME_BETWEEN_REQUESTS = 30

SEND_HEARTBEAT = True

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
                "name": "Spotify Library Manager"
            }
            try:
                print("Heartbeat: " + str(requests.post(getRegistryURL() + "/heartbeat", json=data)), flush=True)
            except Exception as e:
                print("Heartbeat Failed: ", e, flush=True)
            count = 0
        count += 1
        time.sleep(1)


@app.route('/userPlaylists')
def userPlaylists():
    return api.getPlaylists(flask.request.args.get("userToken"))


@app.route('/export')
def exportPlaylist():
    # TODO Export into common format
    return api.getPlaylist(flask.request.args.get("userToken"), flask.request.args.get("playlistId"))


@app.route('/import', methods=['POST'])
def importPlaylist():
    # TODO import common format and create a new playlist based of it
    return "Spotify import endpoint"


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


@app.route('/clientId')
def clientId():
    return api.getClientID()


@app.route('/getUserToken')
def getUserToken():
    response = api.getUserAuthenticationToken(flask.request.args.get("code"), flask.request.args.get("redirect_uri"))
    if response.ok:
        return response.json()
    else:
        print("ERROR", file=sys.stdout, flush=True)
        return flask.Response(response.json(), status=response.status_code, mimetype="application/json")


# TODO test route - delete later
@app.route("/createPlaylist", methods=["POST"])
def createPlaylist():
    p = flask.request.json
    api.createPlaylist(p["userToken"],
                       p["playlistName"],
                       p["playlistDescription"],
                       p["public"],
                       p["tracks"])
    return flask.Response(status=200)


if __name__ == '__main__':
    t1 = threading.Thread(target=sendHeartbeat)
    t1.start()
    app.run(host='0.0.0.0', port=3001)

    # unregisters the service from the registry on stop
    SEND_HEARTBEAT = False
    endRequest = {
        "url": os.environ.get('PROVIDER_URL'),
        "type": "unregister",
        "name": "Spotify Library Manager"
    }
    requests.post(getRegistryURL() + "/heartbeat", json=endRequest)
    t1.join()
