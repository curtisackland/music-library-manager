import os
import sys
import threading
import requests
import time
import flask
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

TIME_BETWEEN_REQUESTS = 30

SEND_HEARTBEAT = True


def sendHeartbeat() -> None:
    global SEND_HEARTBEAT
    while SEND_HEARTBEAT:
        data = {
            "url": os.environ.get('URL'),
            "type": "register",
            "name": "Apple Library Manager"
        }
        print(requests.post(os.environ.get('REGISTRY_URL'), json=data))
        time.sleep(TIME_BETWEEN_REQUESTS)


if __name__ == '__main__':
    t1 = threading.Thread(target=sendHeartbeat)
    t1.start()
    app.run(host='0.0.0.0', port=3001)

    # unregisters the service from the registry on stop
    SEND_HEARTBEAT = False
    endRequest = {
        "url": os.environ.get('URL'),
        "type": "unregister",
        "name": "Apple Library Manager"
    }
    requests.post(os.environ.get('REGISTRY_URL'), json=endRequest)
    t1.join()
