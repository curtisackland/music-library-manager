<script setup>
</script>

<template>
  <nav class="navbar navbar-expand-lg ">
    <RouterLink to="/" style="padding: 10px;"><img src="https://media.tenor.com/Nfct9RreQfUAAAAd/dog-meme.gif" height="64" width="64" style="border-radius: 10px"/></RouterLink>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav">
        <li><RouterLink to="/other">Other</RouterLink></li>
      </ul>
    </div>
  </nav>
</template>

<style scoped>

nav {
  background-color: #AAAABB;
}

nav ul li a img {
  height: 60px;
}
</style>

