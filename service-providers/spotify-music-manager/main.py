import os
import sys
import threading
import requests
import time
import flask
from flask_cors import CORS
import SpotifyAPI

app = flask.Flask(__name__)
CORS(app)

api = SpotifyAPI.SpotifyAPI()

TIME_BETWEEN_REQUESTS = 30

SEND_HEARTBEAT = True


def sendHeartbeat() -> None:
    global SEND_HEARTBEAT
    count = TIME_BETWEEN_REQUESTS
    while SEND_HEARTBEAT:
        if count >= TIME_BETWEEN_REQUESTS:
            data = {
                "url": os.environ.get('URL'),
                "type": "register",
                "name": "Spotify Library Manager"
            }
            print("Heartbeat: " + str(requests.post(os.environ.get('REGISTRY_URL'), json=data)), flush=True)
            count = 0
        count += 1
        time.sleep(1)


@app.route('/userPlaylists')
def userPlaylists():
    return api.getPlaylists(flask.request.args.get("userToken"))


@app.route('/userPlaylist')
def playlist():
    return api.getPlaylist(flask.request.args.get("userToken"), flask.request.args.get("playlist_id"))

@app.route('/export')
def playlist():
    # TODO return common format on export
    return api.getPlaylist(flask.request.args.get("playlist_id"))


@app.route('/import')
def playlist():
    # TODO import common format and create a new playlist based of it
    return "import endpoint"


@app.route('/shuffle', methods=['POST'])
def shuffle():
    print(flask.request.json)
    return flask.request.json


@app.route('/sort', methods=['POST'])
def sort():
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
        "url": os.environ.get('URL'),
        "type": "unregister",
        "name": "Spotify Library Manager"
    }
    requests.post(os.environ.get('REGISTRY_URL'), json=endRequest)
    t1.join()
