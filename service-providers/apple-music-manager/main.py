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

def shuffle (songFrequency = 0, artistFrequency = 0, genreFrequency = 0, albumFrequency = 0, data=[], RequestedPlaylistSize = 0, minTime = 0, maxTime = 0):

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

    def checkFrequency(attributeDict, attributeKeyList, ID, attribute):
        if attribute == "genre" or attribute == "artist":
            if attribute == "genre":
                if "EMPTY" in attributeDict:
                    if ID in attributeDict["EMPTY"][SONGLIST]:
                        return True
            keys = []
            for key in attributeKeyList:
                if ID in attributeDict[key][SONGLIST]:
                    if attributeDict[key][FREQUENCY_COUNTER] <= 0:
                        keys.append(key)
                    else:
                        return False
            
            return keys

        else:
            for key in attributeKeyList:
                if ID in attributeDict[key][SONGLIST]:
                    if attributeDict[key][FREQUENCY_COUNTER] <= 0:
                        return key
                    else:
                        return False


    def reduceFrequencyCounter(attributeDict, attributeKeyList, excludedKey):
        for key in attributeKeyList:
            if isinstance(excludedKey, list):
                if key in excludedKey:
                    continue
            else:
                if key == excludedKey:
                    continue
                    
            attributeDict[key][FREQUENCY_COUNTER] -= 1
    
    if RequestedPlaylistSize == 0:
        raise Size0
    
    songDict = {}
    artistDict = {}
    genreDict = {}
    albumDict = {}

    # sorts songs by adding them to dictionaries
    appendName_index = 0
    for song in data:
        if song['songLength'] >= (minTime * 1000) and song['songLength'] <= (maxTime * 1000):

            # Appends an integer to a duplicate song name to make them unique
            if song['songName'] in songDict:
                newName = song['songName'] + str(appendName_index)
                songDict.setdefault(newName, [0, []])
                songDict[newName][SONGLIST].append(song["appleSongId"])
                appendName_index += 1
            else:
                songDict.setdefault(song['songName'], [0, []])
                songDict[song['songName']][SONGLIST].append(song["appleSongId"])

            for artist in song['artists']:
                artistDict.setdefault(artist, [0, []])
                artistDict[artist][SONGLIST].append(song["appleSongId"])

            if not song['genres']:
                genreDict.setdefault("EMPTY", [0, []])
                genreDict["EMPTY"][SONGLIST].append(song["appleSongId"])
            else:
                for genre in song['genres']:
                    genreDict.setdefault(genre, [0, []])
                    genreDict[genre][SONGLIST].append(song["appleSongId"])

            albumDict.setdefault(song['album'], [0, []])
            albumDict[song['album']][SONGLIST].append(song["appleSongId"])

            
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

            associatedArtist = checkFrequency(artistDict, artistKeyList, ID, "artist")
            associatedGenre = checkFrequency(genreDict, genreKeyList, ID, "genre")
            associatedAlbum = checkFrequency(albumDict, albumKeyList, ID, "album")
            
            if associatedArtist and associatedGenre and associatedAlbum:

                finalPlaylist_array.append(ID)

                reduceFrequencyCounter(songDict, songKeyList, associatedName)
                songDict[associatedName][FREQUENCY_COUNTER] = songFrequency

                reduceFrequencyCounter(artistDict, artistKeyList, associatedArtist)
                for artist in associatedArtist:
                    artistDict[artist][FREQUENCY_COUNTER] = artistFrequency

                reduceFrequencyCounter(albumDict, albumKeyList, associatedAlbum)
                albumDict[associatedAlbum][FREQUENCY_COUNTER] = albumFrequency

                if not isinstance(associatedGenre, bool):
                    reduceFrequencyCounter(genreDict, genreKeyList, associatedGenre)
                    for genre in associatedGenre:
                        genreDict[genre][FREQUENCY_COUNTER] = genreFrequency
                else:
                    reduceFrequencyCounter(genreDict, genreKeyList, "EMPTY")

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

    data_ID_array = [d["appleSongId"] for d in data]

    # creates final JSON to output
    for ID in finalPlaylist_array:
        for i in range(0, len(data_ID_array)):
            if ID == data_ID_array[i]:
                finalPlaylist.append(data[i])

    return finalPlaylist

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
    rJson = flask.request.json
    api.createPlaylistFromCommonFormat(rJson["userToken"], rJson["playlistTitle"], "", rJson["songList"])
    return "Success"


@app.route('/shuffle', methods=['POST'])
def shuffleEndpoint():

    commonFormat = getCommonFormatSongsFromPlaylists(flask.request.args.get("userToken"),
                                                     flask.request.json.get("playlistIds"))

    try:
        commonFormat = shuffle(
            songFrequency=int(flask.request.json.get('songFreq')),
            artistFrequency=int(flask.request.json.get('artistFreq')),
            genreFrequency=int(flask.request.json.get('genreFreq')),
            albumFrequency=int(flask.request.json.get('albumFreq')),
            data=commonFormat,
            RequestedPlaylistSize=int(flask.request.json.get('lengthOfPlaylist')),
            minTime=int(flask.request.json.get('minSongLength')),
            maxTime=int(flask.request.json.get('maxSongLength')))

        api.createPlaylistFromCommonFormat(flask.request.args.get("userToken"),
                                           flask.request.json.get('newPlaylistName'), "", commonFormat)
    except Exception as e:
        return str(e)

    return "Success"


@app.route('/sort', methods=['POST'])
def sort():
    attributeDictionary = {
        "Song Name": ["songName", flask.request.json.get("songNameOrder")],
        "Album Name": ["album", flask.request.json.get("albumNameOrder")],
        "Genre Name": ["genres", flask.request.json.get("genreNameOrder")],
        "Artist Name": ["artists", flask.request.json.get("artistNameOrder")],
        "Song Length": ["songLength", flask.request.json.get("songLengthOrder")],
        "Song Release Date": ["releaseDate", flask.request.json.get("songReleaseDateOrder")]
    }


    def sorting(songs, sortPriority):
        target = attributeDictionary[sortPriority[0]][0]
        order = attributeDictionary[sortPriority[0]][1]
        playlist = []
        
        if order == "None":
            if len(sortPriority) == 0:
                return songs
            return sorting(songs, sortPriority[1:])
    
        for song in songs:
            found = False
            i = 0

            while i < len(playlist) and not found:
                res = compare(song[target], playlist[i][0][target], target, order)

                # The position after is found at i.
                if res == 0:
                    found = True
                    playlist.insert(i, [song])
                # The position at i is equivalent.
                elif res == 1:
                    found = True
                    playlist[i].append(song)

                i += 1

            # The end of the playlist so appends to end.
            if not found:
                playlist.append([song])

        # Nothing left to sort by.
        if len(sortPriority) == 0:
            return squash(playlist)

        # Sorts the songs with equivalent values with the next sort priority.
        for i in range(0, len(playlist)):
            if len(playlist[i]) > 1:
                playlist[i] = sorting(playlist[i], sortPriority[1:])

        return squash(playlist)


    def compare(one, two, attribute, order):
        # Appends the attributes that come as a list to make a string.
        if attribute == "artists" or attribute == "genres":
            tmp = ""
            for item in one:
                tmp += item
            one = tmp

            tmp = ""
            for item in two:
                tmp += item
            two = tmp

        # Compare.
        if order == "DESC" and one > two:
            return 0
        elif order == "ASC" and one < two:
            return 0
        elif one == two:
            return 1
        
        return -1


    def squash(songs):
        squashedList = []

        for subList in songs:
            for song in subList:
                squashedList.append(song)

        return squashedList


    songsList = getCommonFormatSongsFromPlaylists(flask.request.args.get("userToken"),
                                                  flask.request.json.get("playlistIds"))
    
    commonFormat = sorting(songsList, flask.request.json.get("sortPriority"))

    api.createPlaylistFromCommonFormat(flask.request.args.get("userToken"),
                                       flask.request.json.get("newPlaylistName"),
                                       "",
                                       commonFormat)


    return "Success"


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
