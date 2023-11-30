import os
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


def sendHeartbeat() -> None:
    global SEND_HEARTBEAT
    count = TIME_BETWEEN_REQUESTS
    while SEND_HEARTBEAT:
        if count >= TIME_BETWEEN_REQUESTS:
            data = {
                "url": os.environ.get('URL'),
                "type": "register",
                "name": "Apple Library Manager"
            }
            print("Heartbeat: " + str(requests.post(os.environ.get('REGISTRY_URL'), json=data)), flush=True)
            count = 0
        count += 1
        time.sleep(1)


@app.route("/getDeveloperToken")
def getDeveloperToken():
    return AppleAPI.getBearerToken()

@app.route("/getPlaylists")
def getPlaylists():
    return api.getPlaylists(flask.request.args.get("user_token"))

if __name__ == '__main__':
    t1 = threading.Thread(target=sendHeartbeat)
    t1.start()
    app.run(host='0.0.0.0', port=3002)

    # unregisters the service from the registry on stop
    SEND_HEARTBEAT = False
    endRequest = {
        "url": os.environ.get('URL'),
        "type": "unregister",
        "name": "Apple Library Manager"
    }
    requests.post(os.environ.get('REGISTRY_URL'), json=endRequest)
    t1.join()
