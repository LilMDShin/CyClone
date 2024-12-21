<script setup lang="ts">
import { ref } from 'vue';
import HelloWorld from './components/HelloWorld.vue'
import Top from './components/Top.vue'
import Earth from './components/Earth.vue';
import Navbar from './components/Navbar.vue';

const currentFilter = ref<string>('now');

function filterCyclones(filterType: string) {
  currentFilter.value = filterType;
  console.log("hii")
  console.log(currentFilter.value);
}
</script>

<template>
  <div>
    <!-- <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a> -->
    
  </div>
  <Top />
  <Navbar @filterCyclones="filterCyclones"/>
  <Earth :filter="currentFilter" />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
