<template>
<h1>Hello World</h1>
</template>

<script>
  import axios from "axios"
  export default {
    name: "TestPage",
    methods: {
      async fetchData() {
        //this.tableData = (await axios.get("http://localhost:8080")).data;
        //this.tableHead = Object.keys(this.tableData[0]);
      }
    },
    data() {
      return {
        tableHead: null,
        tableData: null
      };
    },
    mounted() {
      this.fetchData();
    }
  }
</script>

<style scoped>

</style>
