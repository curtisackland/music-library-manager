
<template>
  <h1>Spotify Library Manager</h1>
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
        this.playlists = (await axios.get("http://localhost:3001/playlists?username=verycreepy")).data;
      },
      async downloadJson(id) {
        try {
          // Make an Axios request to fetch JSON data
          const response = await axios.get('http://localhost:3001/playlist?playlist_id=' + id); // Replace with your API endpoint

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
    },
    data() {
      return {
        appToken: "some api key",
        playlists: null
      }
    },
    mounted() {
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
