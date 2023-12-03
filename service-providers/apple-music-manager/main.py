import os
import re
import threading
import requests
import time
import flask
from flask_cors import CORS

import AppleAPI

app = flask.Flask(__name__)
CORS(app)

api = AppleAPI.AppleAPI()

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
                "name": "Apple Library Manager"
            }
            try:
                print("Heartbeat: " + str(requests.post(getRegistryURL() + "/heartbeat", json=data)), flush=True)
            except Exception as e:
                print("Heartbeat Failed: ", e, flush=True)
            count = 0
        count += 1
        time.sleep(1)


@app.route("/userPlaylists")
def userPlaylists():
    return api.getPlaylists(flask.request.args.get("userToken"))


@app.route('/export')
def exportPlaylist():
    # TODO export common format of chosen playlist
    return "Apple export endpoint"  # api.getPlaylist(flask.request.args.get("userToken"), flask.request.args.get("playlistId"))


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
