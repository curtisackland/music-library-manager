import flask
from flask_cors import CORS
import SpotifyAPI
app = flask.Flask(__name__)
CORS(app)
import sys

api = SpotifyAPI.SpotifyAPI()

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
    app.run(host='0.0.0.0', port=3001)
    #TODO: Add deregistration heartbeat here

