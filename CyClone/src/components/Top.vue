<script setup lang="ts">
import { defineProps } from 'vue';


defineProps({
  title: {
    type: String,
    default: 'CyClone',
  },
  logo: {
    type: String,
    default: "../assets/logo_cy.png",
  },
});
</script>

<template>
  <header class="header">
    <div class="logo-container">
      
      <img v-if=logo src="../assets/logo.png" class="logo" alt="Logo" />
      <h1 class="title">{{ title }}</h1>
    </div>

  </header>

</template>

<style scoped>

.header {
  width : 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #030303;
  place-content: center;
  
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  width: 40px;
  height: 40px;
  margin-right: 0.5rem;
}

.title {

  font-size: 2.5rem;
  color: #3465A4;
}

</style>