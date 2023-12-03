import os
import re
import threading
import requests
import time
import flask
import json
import random
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
            newSong["artists"] = [track["attributes"]["artistName"]]
            newSong["genres"] = track["attributes"]["genreNames"]
            newSong["album"] = track["attributes"]["albumName"]
            newSong["songLength"] = track["attributes"]["durationInMillis"]
            newSong["releaseDate"] = track["attributes"]["releaseDate"]
            newSong["appleSongId"] = track["id"]

            songs.append(newSong)

    return songs

def shuffle (songFrequency = 0, artistFrequency = 0, genreFrequency = 0, albumFrequency = 0, File="", RequestedPlaylistSize = 0, minTime = 0, maxTime = 0):

    FREQUENCY_COUNTER = 0
    SONGLIST = 1

    class Size0(Exception):
        def __init__(self, msg='Requested Playlist Size is 0', *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class NoSongs(Exception):
        def __init__(self, msg='No Songs in Playlist', *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class HighSongFrequency(Exception):
        def __init__(self, msg="Input Song Frequency is too high", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class HighArtistFrequency(Exception):
        def __init__(self, msg="Input Artist Frequency is too high", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class HighGenreFrequency(Exception):
        def __init__(self, msg="Input Genre Frequency is too high", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class HighAlbumFrequency(Exception):
        def __init__(self, msg="Input Album Frequency is too high", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class ShuffleDeadlock(Exception):
        def __init__(self, msg="Deadlock occurred during Shuffle. Try changing frequency values.", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    def checkFrequency(attributeDict, attributeKeyList, ID):
        for key in attributeKeyList:
            if ID in attributeDict[key][SONGLIST]:
                if attributeDict[key][FREQUENCY_COUNTER] <= 0:
                    return key
                else:
                    return False


    def reduceFrequencyCounter(attributeDict, attributeKeyList, excludedKey):
        for key in attributeKeyList:
            if key == excludedKey:
                continue
            attributeDict[key][FREQUENCY_COUNTER] -= 1
    
    if RequestedPlaylistSize == 0:
        raise Size0
    
    f = open(File)
    data = json.load(f)
    
    songDict = {}
    artistDict = {}
    genreDict = {}
    albumDict = {}

    # sorts songs by adding them to dictionaries
    for song in data:
        if song['songLength'] >= minTime and song['songLength'] <= maxTime:

            songDict.setdefault(song['songName'], [0, []])
            songDict[song['songName']][SONGLIST].append(song['appleSongId'])

            artistDict.setdefault(song['artist'], [0, []])
            artistDict[song['artist']][SONGLIST].append(song['appleSongId'])

            genreDict.setdefault(song['genre'], [0, []])
            genreDict[song['genre']][SONGLIST].append(song['appleSongId'])

            albumDict.setdefault(song['album'], [0, []])
            albumDict[song['album']][SONGLIST].append(song['appleSongId'])

    if not bool(songDict):
        raise NoSongs

    # randomly shuffle the songlist of each dict entry to introduce randomness to output
    for dict in [songDict, artistDict, genreDict, albumDict]:
        for element in dict:
            random.shuffle(dict[element][SONGLIST])

    # creates shuffled key list of song dict
    songKeyList = list(songDict.keys())
    random.shuffle(songKeyList)
    new_songDict = {}
    for key in songKeyList:
        new_songDict[key] = songDict[key]
    songDict = new_songDict

    finalPlaylist_array = []

    artistKeyList = list(artistDict.keys())
    genreKeyList = list(genreDict.keys())
    albumKeyList = list(albumDict.keys())

    if (len(songKeyList) <= songFrequency):
        raise HighSongFrequency
    elif (len(artistKeyList) <= artistFrequency):
        raise HighArtistFrequency
    elif (len(genreKeyList) <= genreFrequency):
        raise HighGenreFrequency
    elif (len(albumKeyList) <= albumFrequency):
        raise HighAlbumFrequency

    index = 0
    Timeout = 0
    initiateLinearSearch = False
    
    # Randomly check songs in playlist to see if song can be added to final playlist based on frequency rules.
    # If none found by random, then check through playlist linearly.
    # If none found through linear check, raise exception.
    while (len(finalPlaylist_array) != RequestedPlaylistSize):

        ID = ''
        associatedName =''
        associatedArtist = ''
        associatedGenre = ''
        associatedAlbum = ''

        if songDict[songKeyList[index]][FREQUENCY_COUNTER] <= 0:

            associatedName = songKeyList[index]
            ID = songDict[songKeyList[index]][SONGLIST][0]

            associatedArtist = checkFrequency(artistDict, artistKeyList, ID)
            associatedGenre = checkFrequency(genreDict, genreKeyList, ID)
            associatedAlbum = checkFrequency(albumDict, albumKeyList, ID)
            
            if associatedArtist and associatedGenre and associatedAlbum:

                finalPlaylist_array.append(ID)

                reduceFrequencyCounter(songDict, songKeyList, associatedName)
                reduceFrequencyCounter(artistDict, artistKeyList, associatedArtist)
                reduceFrequencyCounter(genreDict, genreKeyList, associatedGenre)
                reduceFrequencyCounter(albumDict, albumKeyList, associatedAlbum)

                songDict[associatedName][FREQUENCY_COUNTER] = songFrequency
                artistDict[associatedArtist][FREQUENCY_COUNTER] = artistFrequency
                genreDict[associatedGenre][FREQUENCY_COUNTER] = genreFrequency
                albumDict[associatedAlbum][FREQUENCY_COUNTER] = albumFrequency

                Timeout = 0
                initiateLinearSearch = False

        if  initiateLinearSearch:
            if Timeout > len(songKeyList):
                raise ShuffleDeadlock
            index = (index + 1) % len(songKeyList)
        else:
            if Timeout > (len(songKeyList) * 3):
                initiateLinearSearch = True
                Timeout = 0
            index = random.randint(0, len(songKeyList) - 1)
            
        Timeout += 1
        

    finalPlaylist = []

    data_ID_array = [d['appleSongId'] for d in data]

    # creates final JSON to output
    for ID in finalPlaylist_array:
        for i in range(0, len(data_ID_array)):
            if ID == data_ID_array[i]:
                finalPlaylist.append(data[i])

    outputFILE = json.dumps(finalPlaylist, indent = 2)

    return outputFILE

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
