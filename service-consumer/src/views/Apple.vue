<template>
  <h1>Apple Music takes 2 HOURS to update</h1>
  {{ $store.getters.getBackendURL }}
  {{ eq }}
</template>

<script>
import axios from "axios";


export default {
  name: "Apple",
  methods: {
    async getMusicUserToken() {
      return await MusicKit.getInstance().authorize();
    },
    async exampleQuery() {
      let x = await axios.get("http://localhost:3002/getPlaylists", {params:{"user_token":await this.getMusicUserToken()}});
      console.log(x);
      console.log(x.data);
      return x;
    }
  },
  data() {
    return {
      eq:null,
    }
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

    this.eq = await this.exampleQuery()
  }
}
</script>

