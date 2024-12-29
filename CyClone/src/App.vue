<script setup lang="ts">
import { ref } from 'vue';
import Top from './components/Top.vue'
import Earth from './components/Earth.vue';

const currentFilter = ref<string>('now');


</script>

<template>
  <div>
    <!-- <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a> -->
    
  </div>
  <Top />
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
