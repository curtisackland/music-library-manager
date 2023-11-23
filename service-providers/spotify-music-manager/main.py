from flask import Flask
from flask import request
from flask_cors import CORS
import SpotifyAPI
app = Flask(__name__)
CORS(app)

api = SpotifyAPI.SpotifyAPI()

@app.route('/playlists')
def playlists():
    return api.getPlaylists(request.args.get("username"))

@app.route('/playlist')
def playlist():
    return api.getPlaylist(request.args.get("playlist_id"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)

