import copy
from datetime import datetime
import re
import json
import signal
import flask
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

TIME_OUT_TIME = 60

# Format looks like {"provider name": "location of provider", "provider name2": "location of provider2"}
PROVIDERS = {}
# Format looks like {"provider name": "time", "provider name2": "time2"}
PROVIDERS_LAST_HEARTBEAT_TIME = {}


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    try:
        if flask.request.json.get('type') == 'register':
            if not flask.request.json.get('name') or not flask.request.json.get('url'):
                raise Exception
            PROVIDERS[flask.request.json.get("name")] = flask.request.json.get("url")
            PROVIDERS_LAST_HEARTBEAT_TIME[flask.request.json.get("name")] = datetime.now()

        elif flask.request.json.get('type') == 'unregister':
            if flask.request.json.get("name") in PROVIDERS:
                PROVIDERS.pop(flask.request.json.get("name"))
                PROVIDERS_LAST_HEARTBEAT_TIME.pop(flask.request.json.get("name"))

        else:
            raise Exception
    except:
        return "Error"

    return "Success"


@app.route('/search')
def search():
    removeTimedOutProviders()
    if not flask.request.args.get("query"):  # if no query is provided just return all providers
        return json.dumps({"names": [key for key in PROVIDERS.keys()]})

    query = flask.request.args.get("query")
    pattern = re.compile(f".*{re.escape(query)}.*")
    matchedNames = {"names": [key for key in PROVIDERS.keys() if pattern.search(key)]}
    return json.dumps(matchedNames)


# Remove providers that have not sent a heartbeat in the time specified by TIME_OUT_TIME
def removeTimedOutProviders():
    currentTime = datetime.now()
    tempDict = copy.deepcopy(PROVIDERS_LAST_HEARTBEAT_TIME)
    for key, value in tempDict.items():
        timeDifference = currentTime - value
        if timeDifference.total_seconds() > TIME_OUT_TIME:
            PROVIDERS.pop(key)
            PROVIDERS_LAST_HEARTBEAT_TIME.pop(key)


@app.route('/location')
def location():
    if not flask.request.args.get("name") in PROVIDERS:
        return "Error"

    return json.dumps({"location": PROVIDERS[flask.request.args.get("name")]})

def raiseSIGINT(a, b):
    print("Terminating", flush=True)
    raise KeyboardInterrupt # stop flask

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, raiseSIGINT)
    app.run(host='0.0.0.0', port=3000)
