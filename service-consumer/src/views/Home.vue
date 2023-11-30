<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12 d-flex justify-content-center align-items-center" style="min-height: 100vh;">
        <div>
          {{ $store.getters.getBackendURL}}
          <h1 class="w-100">Provider Search</h1>
          <input class="w-100" type="text" v-model="input" @input="search" placeholder="Search providers..." />
          <div class="item mt-2" v-for="provider in providers">
            <button class="btn btn-primary w-100" @click="goToProvider(provider)">{{ provider }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios"
export default {
  name: "Home",
  methods: {
    async fetchData() {
      this.providers = (await axios.get("http://localhost:3000/search")).data.names;
    },
    async search() {
      this.providers = (await axios.get("http://localhost:3000/search?query=" + encodeURIComponent(this.input))).data.names;
    },
    async goToProvider(provider) {
      if (provider.includes('Spotify')) {
        this.$store.dispatch('updateBackendURL', (await axios.get("http://localhost:3000/location?name=" + encodeURIComponent(provider))).data.location);
        this.$router.push('/spotify');
      } else if (provider.includes('Apple')) {
        this.$store.dispatch('updateBackendURL', (await axios.get("http://localhost:3000/location?name=" + encodeURIComponent(provider))).data.location);
        this.$router.push('/apple');
      }
    },
  },
  data() {
    return {
      input: null,
      providers: [],
    };
  },
  mounted() {
    this.fetchData();
  }
}
</script>

<style>

</style>
