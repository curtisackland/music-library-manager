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
    while SEND_HEARTBEAT:
        data = {
            "url": os.environ.get('URL'),
            "type": "register",
            "name": "Spotify Library Manager"
        }
        print(requests.post(os.environ.get('REGISTRY_URL'), json=data))
        time.sleep(TIME_BETWEEN_REQUESTS)


@app.route('/playlists')
def playlists():
    return api.getPlaylists(flask.request.args.get("username"))


@app.route('/playlist')
def playlist():
    return api.getPlaylist(flask.request.args.get("playlist_id"))


@app.route('/client_id')
def client_id():
    return api.getClientID()


@app.route('/get_user_token')
def get_user_token():
    response = api.getUserAuthenticationToken(flask.request.args.get("code"), flask.request.args.get("redirect_uri"))
    if response.ok:
        return response.json()
    else:
        print("ERROR", file=sys.stdout, flush=True)
        return flask.Response(response.json(), status=response.status_code, mimetype="application/json")


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
