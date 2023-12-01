<template>
  <h1>Apple Music takes 2 HOURS to update</h1>
  {{ $store.getters.getBackendURL }}
  <div v-if="loadPage && playlists">

    <!-- Export playlist table -->
    <table class="mt-3">
      <thead>
      <tr>
        <th>Playlist</th>
        <th>Export</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="row in playlists">
        <td><span>{{row.value}}</span></td>
        <td><button class="btn btn-primary" @click="downloadJson(row.key)">Download JSON</button></td>
      </tr>
      </tbody>
    </table>

    <!-- Import playlist -->
    <div class="flex-column mt-5 w-100">
      <span><b> Upload a file to import:&nbsp;&nbsp;&nbsp;&nbsp;</b></span>
      <input type="file" ref="fileInput" />
      <button class="btn btn-primary" @click="importPlaylist">Import</button>
    </div>

    <!-- Shuffler Section -->

    <!-- Playlist Dropdown -->
    <h1 class="mt-5">Shuffler</h1>
    <multiselect
        class="w-50"
        v-model="shuffleSelectedPlaylists"
        :options="playlists"
        :multiple="true"
        placeholder="Choose playlists to shuffle"
        :clear-on-select="false"
        :close-on-select="false"
        label="value"
        track-by="key">
    </multiselect>

    <label class="mt-3 p-2">New playlist name: </label>
    <input type="text" v-model="shuffleNewPlaylistName" placeholder="New name"/>

    <div>
      <label class="mt-3 p-2">Minimum Song Length (seconds): </label>
      <input type="number" min="0" v-model="shuffleMinSongLength"/>
    </div>

    <div>
      <label class="mt-3 p-2">Maximum Song Length (seconds): </label>
      <input type="number" min="0" max="1000" v-model="shuffleMaxSongLength"/>
    </div>

    <div>
      <label class="mt-3 p-2">Song Frequency: </label>
      <input type="number" min="0" max="100" v-model="shuffleSongFreq"/>
    </div>

    <div>
      <label class="mt-3 p-2">Album Frequency: </label>
      <input type="number" min="0" max="100" v-model="shuffleAlbumFreq"/>
    </div>

    <div>
      <label class="mt-3 p-2">Artist Frequency: </label>
      <input type="number" min="0" max="100" v-model="shuffleArtistFreq"/>
    </div>

    <div>
      <label class="mt-3 p-2">Genre Frequency: </label>
      <input type="number" min="0" max="100" v-model="shuffleGenreFreq"/>
    </div>

    <div>
      <label class="mt-3 p-2">Length of new playlist: </label>
      <input type="number" min="0" max="100" v-model="shuffleLengthOfPlaylist"/>
    </div>

    <button class="btn btn-primary mt-3" @click="shuffleSubmit">Submit</button>

    <label class="error">{{ shuffleErrors }}</label>


    <!-- Sorter Section -->

    <h1 class="mt-5">Sorter</h1>
    <multiselect
        class="w-50"
        v-model="sortSelectedPlaylists"
        :options="playlists"
        :multiple="true"
        placeholder="Choose playlists to sort"
        :clear-on-select="false"
        :close-on-select="false"
        label="value"
        track-by="key">
    </multiselect>

    <label class="mt-3 p-2">New playlist name: </label>
    <input type="text" v-model="sortNewPlaylistName" placeholder="New name"/>

    <div>
      <label class="mt-3 p-2">Sort alphabetically by song name: </label>
      <multiselect class="w-50" v-model="sortSongNameOrder" :options="orders" :clear-on-select="false" />
    </div>

    <div>
      <label class="mt-3 p-2">Sort alphabetically by album name: </label>
      <multiselect class="w-50" v-model="sortAlbumNameOrder" :options="orders" :clear-on-select="false" />
    </div>

    <div>
      <label class="mt-3 p-2">Sort alphabetically by genre name: </label>
      <multiselect class="w-50" v-model="sortGenreNameOrder" :options="orders" :clear-on-select="false" />
    </div>

    <div>
      <label class="mt-3 p-2">Sort alphabetically by artist name: </label>
      <multiselect class="w-50" v-model="sortArtistNameOrder" :options="orders" :clear-on-select="false" />
    </div>

    <div>
      <label class="mt-3 p-2">Sort alphabetically by song length: </label>
      <multiselect class="w-50" v-model="sortSongLengthOrder" :options="orders" :clear-on-select="false" />
    </div>

    <div>
      <label class="mt-3 p-2">Sort alphabetically by song release date: </label>
      <multiselect class="w-50" v-model="sortSongReleaseDateOrder" :options="orders" :clear-on-select="false" />
    </div>

    <div>
      <label class="mt-3 p-2">Length of new playlist: </label>
      <input type="number" min="0" max="100" v-model="sortLengthOfPlaylist"/>
    </div>

    <div>
      <label class="mt-3 p-2">Select what order your sorting should be applied: </label>
      <multiselect
          class="w-50"
          v-model="sortPriority"
          :options="sortOptions"
          :multiple="true"
          placeholder="Choose order for sorting"
          :clear-on-select="false"
          :close-on-select="false">
      </multiselect>
    </div>

    <button class="btn btn-primary mt-3" @click="sortSubmit">Submit</button>

    <label class="error">{{ sortErrors }}</label>

  </div>
</template>

<script>
import axios from "axios";

import Multiselect from 'vue-multiselect';
export default {
  name: "Apple",
  components: {
    Multiselect
  },
  data() {
    return {
      loadPage: false,
      shuffleSelectedPlaylists: [],
      playlists: [],
      shuffleNewPlaylistName: null,
      shuffleMinSongLength: 0,
      shuffleMaxSongLength: 1000,
      shuffleSongFreq: 0,
      shuffleAlbumFreq: 0,
      shuffleArtistFreq: 0,
      shuffleGenreFreq: 0,
      shuffleLengthOfPlaylist: 100,
      shuffleErrors: null,
      // sort vars
      orders: ['ASC', 'DESC', 'None'],
      sortOptions: ['Song Name', 'Album Name', 'Genre Name', 'Artist Name', 'Song Length', 'Song Release Date'],
      sortSelectedPlaylists: [],
      sortNewPlaylistName: null,
      sortSongNameOrder: "None",
      sortAlbumNameOrder: "None",
      sortGenreNameOrder: "None",
      sortArtistNameOrder: "None",
      sortSongLengthOrder: "None",
      sortSongReleaseDateOrder: "None",
      sortLengthOfPlaylist: 100,
      sortPriority: [],
      sortErrors: null,
    }
  },
  methods: {
    async shuffleSubmit() {
      this.shuffleErrors = null;
      if (this.shuffleSelectedPlaylists.length === 0) {
        this.shuffleErrors = "No playlists selected";
      } else if (this.shuffleNewPlaylistName == null) {
        this.shuffleErrors = "Enter a new playlist name";
      } else if (this.shuffleMinSongLength < 0) {
        this.shuffleErrors = "Invalid minimum song length";
      } else if (this.shuffleMaxSongLength < 0) {
        this.shuffleErrors = "Invalid maximum song length";
      } else if (this.shuffleSongFreq < 0 || this.shuffleSongFreq > 100) {
        this.shuffleErrors = "Invalid song frequency";
      } else if (this.shuffleAlbumFreq < 0 || this.shuffleAlbumFreq > 100) {
        this.shuffleErrors = "Invalid album frequency";
      } else if (this.shuffleArtistFreq < 0 || this.shuffleArtistFreq > 100) {
        this.shuffleErrors = "Invalid artist frequency";
      } else if (this.shuffleGenreFreq < 0 || this.shuffleGenreFreq > 100) {
        this.shuffleErrors = "Invalid genre frequency";
      } else if (this.shuffleLengthOfPlaylist < 0 || this.shuffleLengthOfPlaylist > 100) {
        this.shuffleErrors = "Invalid playlist length";
      }
      else {
        const playlistIds = [];
        for(let i = 0; i < this.shuffleSelectedPlaylists.length; i++) {
          playlistIds.push(this.shuffleSelectedPlaylists[i].key);
        }
        const submit = axios.post(this.getAppleProviderURL() + '/shuffle', {
              playlistIds: playlistIds,
              newPlaylistName: this.shuffleNewPlaylistName,
              minSongLength: this.shuffleMinSongLength,
              maxSongLength: this.shuffleMaxSongLength,
              songFreq: this.shuffleSongFreq,
              albumFreq: this.shuffleAlbumFreq,
              artistFreq: this.shuffleArtistFreq,
              genreFreq: this.shuffleGenreFreq,
              lengthOfPlaylist: this.shuffleLengthOfPlaylist
            },
            {params: {userToken: await this.getMusicUserToken()}});

        submit.then(async (result) => {
          this.shuffleErrors = "Playlist successfully created";
        }).catch((error) => {
          this.shuffleErrors = "Playlist was not created. Try again.";
        });
      }
    },
    async sortSubmit() {
      this.sortErrors = null;
      if (this.sortSelectedPlaylists.length === 0) {
        this.sortErrors = "No playlists selected";
      } else if (this.sortNewPlaylistName == null) {
        this.sortErrors = "Enter a new playlist name";
      } else if (this.sortLengthOfPlaylist < 0 || this.sortLengthOfPlaylist > 100) {
        this.sortErrors = "Invalid playlist length";
      } else if (this.sortPriority.length === 0) {
        this.sortErrors = "Need to pick what sorts to apply";
      } else {
        const playlistIds = [];
        for(let i = 0; i < this.sortSelectedPlaylists.length; i++) {
          playlistIds.push(this.sortSelectedPlaylists[i].key);
        }
        const submit = axios.post(this.getAppleProviderURL() + '/sort', {
          playlistIds: playlistIds,
          newPlaylistName: this.sortNewPlaylistName,
          songNameOrder: this.sortSongNameOrder,
          albumNameOrder: this.sortAlbumNameOrder,
          genreNameOrder: this.sortGenreNameOrder,
          artistNameOrder: this.sortArtistNameOrder,
          songLengthOrder: this.sortSongLengthOrder,
          songReleaseDateOrder: this.sortSongReleaseDateOrder,
          lengthOfPlaylist: this.sortLengthOfPlaylist,
          sortPriority: this.sortPriority
        },
            {params: {userToken: await this.getMusicUserToken()}});

        submit.then(async (result) => {
          this.sortErrors = "Playlist successfully created";
        }).catch((error) => {
          this.sortErrors = "Playlist was not created. Try again.";
        });
      }
    },
    async fetchPlaylists() {
      // TODO update with playlist common format
      let temp = (await axios.get(this.getAppleProviderURL() + "/userPlaylists", {params: {userToken: await this.getMusicUserToken()}})).data;
      this.playlists = [];
      for(let i = 0; i < temp.data.length; i++) {
        this.playlists.push({key: temp.data[i].id, value: temp.data[i].attributes.name});
      }
    },
    async downloadJson(id) {
      try {
        // TODO get common format from back-end
        // Make an Axios request to fetch JSON data
        const response = await axios.get(this.getAppleProviderURL() + '/export', {params: {userToken: await this.getMusicUserToken(), playlistId: id}});

        // Get the JSON data from the response
        const jsonData = response.data;

        // Convert JSON to a string
        const jsonString = JSON.stringify(jsonData, null, 2);

        // Create a Blob with the JSON string
        const blob = new Blob([jsonString], { type: 'application/json' });

        // Create a link element
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);

        // Set the download attribute with the desired file name
        link.download = 'playlist.json';

        // Append the link to the document
        document.body.appendChild(link);

        // Trigger a click on the link to start the download
        link.click();

        // Remove the link from the document
        document.body.removeChild(link);
      } catch (error) {
        console.error('Error fetching JSON data:', error);
      }
    },
    async importPlaylist() {
      const fileInput = this.$refs.fileInput;
      const file = fileInput.files[0];
      const fileText = file.text();

      fileText.then(async (result) => {
        await axios.post(this.getAppleProviderURL() + '/import', JSON.parse(result), {params: {userToken: await this.getMusicUserToken()}});
      }).catch((error) => {
        console.error(error);
      });
    },
    async getMusicUserToken() {
      return await MusicKit.getInstance().authorize();
    },
    getAppleProviderURL() {
      return $store.getters.getBackendURL;
    },
  },
  async mounted() {
    while (MusicKit == undefined); // Wait for apple music to load
    await MusicKit.configure({
      developerToken: (await axios.get("http://localhost:3002/getDeveloperToken")).data,
      app: {
        name: 'Apple Muisc',
        build: '0.0.1',
      },
    });

    await MusicKit.getInstance().authorize(); // Force login to happen immediately
    this.loadPage = true;

    this.fetchPlaylists();
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
th {
  text-align: center;
  min-width: 100px;
}
.error {
  color: red;
}
</style>

