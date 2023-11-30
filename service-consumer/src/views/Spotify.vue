
<template>
  {{ $store.getters.getBackendURL }}
  <h1>Spotify Library Manager</h1>
  <div><button v-if="!userAccessTokenExists()" @click="getUserAccessToken()">Log in to spotify</button></div>
  <div><button @click="createPlaylist()" :disabled="!userAccessTokenExists()">Create playlist</button></div>
  <div v-if="playlists">
    <table>
      <thead>
      <tr>
        <th>Playlist</th>
        <th>Export</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="row in playlists.items">
        <td><span>{{row.name}}</span></td>
        <td><button class="btn btn-primary" @click="downloadJson(row.id)">Download JSON</button></td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

  import axios from "axios";
  export default {
    name: "Spotify",
    methods: {
      async fetchPlaylists() {
        this.playlists = (await axios.get(this.getSpotifyProviderURL() + "/userPlaylists", {params: {userToken: await this.getUserAccessToken()}})).data;
      },
      async downloadJson(id) {
        try {
          // Make an Axios request to fetch JSON data
          const response = await axios.get(this.getSpotifyProviderURL() + '/playlist?playlist_id=' + id);

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
      async spotifyAccountLogin() { // Redirect to the spotify account login
        const my_client_id = (await axios.get(this.getSpotifyProviderURL() + '/clientId')).data;
        console.log(my_client_id);
        const queryParams = {
          response_type: 'code',
          client_id: my_client_id,
          scope: "user-read-private playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private",
          redirect_uri: this.spotifyRedirectUri(),
          state: "state",
        }
        let queryArray = [];
        for (const k in queryParams) {
          queryArray.push(encodeURIComponent(k) + "=" + encodeURIComponent(queryParams[k]));
        }

        let queryString = queryArray.join("&");
        window.location.href = "https://accounts.spotify.com/authorize?" + queryString;
      },
      async getUserAuthorizationCode(forceRegenerate) { // Try to get the user authorization code, if it does not exist, do login
        if (this.spotifyUserAuthorizationCode == null || forceRegenerate) {
          if (this.getUserAuthorizationCodeQueryParam() == null || forceRegenerate) {
            await this.spotifyAccountLogin();
          }
          this.spotifyUserAuthorizationCode = this.getUserAuthorizationCodeQueryParam();
        }
        return this.spotifyUserAuthorizationCode;
      },
      async getUserAccessTokenRequest(forceRegenerate){ // Request to get the user access token from the authorization code
        const config = {
          code: await this.getUserAuthorizationCode(forceRegenerate),
          redirect_uri: this.spotifyRedirectUri(),
        }
        let token = (await axios.get(this.getSpotifyProviderURL() + "/getUserToken", {params: config})).data
        sessionStorage.setItem("spotifyUserAccessTokenFullData", JSON.stringify(
          {
            token: token,
            expries_after: Date.now() + token.expires_in
          }
        ));
      },
      async getUserAccessToken() { // Get the user access token
        let tokenObject = this.getUserAccessTokenFromSession();

        if (tokenObject == null) { // Generate new token
          try {
            await this.getUserAccessTokenRequest(false);
          } catch (error) {
            await this.getUserAccessTokenRequest(true);
          }
        } else if (tokenObject.expries_after < Date.now()) {
          //TODO: Refresh token
        }

        return this.getUserAccessTokenFromSession().token.access_token;
      },
      async createPlaylist() { // Example of how to create a new playlist using the provider
        const createPlaylistBody = {
          userToken: await this.getUserAccessToken(),
          playlistName: "Create Test Playlist",
          playlistDescription: "Test playlist description",
          public: "true",
          tracks: ["spotify:track:5W8YXBz9MTIDyrpYaCg2Ky", "spotify:track:5xTtaWoae3wi06K5WfVUUH"],
        }
        await axios.post(this.getSpotifyProviderURL() + "/createPlaylist", createPlaylistBody)
      },
      spotifyRedirectUri() {
        return "http://localhost:5173/spotify"; // TODO: Update to environment variable
      },
      getSpotifyProviderURL() {
        return "http://localhost:3001"; // TODO: Update to environment variable
      },
      getUserAuthorizationCodeQueryParam() {
        return this.$route.query.code;
      },
      getUserAccessTokenFromSession() {
        let data = sessionStorage.getItem("spotifyUserAccessTokenFullData");
        if (data != null) {
          return JSON.parse(sessionStorage.getItem("spotifyUserAccessTokenFullData"));
        } 
        return null;
        
      },
      userAccessTokenExists() {
        return this.getUserAccessTokenFromSession() != null && this.getUserAccessTokenFromSession() != "";
      }
    },
    data() {
      return {
        playlists: null,
        spotifyUserAuthorizationCode: null,
      }
    },
    async mounted() {
      await this.getUserAccessToken(); // Force login on load
      if (this.getUserAuthorizationCodeQueryParam()) {
        window.location.href = this.spotifyRedirectUri();
      }
     
      this.fetchPlaylists();
    }
  }
</script>

<style scoped>
th {
  text-align: center;
  min-width: 100px;
}
</style>
