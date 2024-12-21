<script setup lang="ts">
import { defineProps } from 'vue';
import { ref } from 'vue';


const emit = defineEmits<{
  (event: 'filterCyclones', filterType: string): void;
}>();

const activeMode = ref<string>('now'); // Mode actif par défaut

function setActiveMode(mode: string) {
  activeMode.value = mode;
  emit('filterCyclones', mode);
}

</script>

<template>
    <div class="nav-container">
      <div class="topnav">
        <a 
          :class="{ active: activeMode === 'now' }"
          @click="setActiveMode('now')">
          Temps réel
        </a>
        <a 
          :class="{ active: activeMode === 'today' }"
          @click="setActiveMode('today')">
          Aujourd'hui
        </a>
        <a 
          :class="{ active: activeMode === 'others' }"
          @click="setActiveMode('others')">
          Autres
        </a>
      </div>
    </div>
  </template>

  
<style scoped>
.nav-container {
  width: 100%; 
  display: flex;
  justify-content: center; 
  align-items: center; 
  padding: 1rem 0; 
  background-color: #030303;
}

.topnav {
  display: flex; 
  gap: 2rem;
} 

.topnav a {
  color: #fff; 
  text-decoration: none; 
  padding: 0.5rem 1rem; 
  border: 1px solid #5e4dcd; 
  border-radius: 6px; 
  background-color: transparent;
  font-size: 1.2rem; 
  transition: background-color 0.3s ease; 
}

.topnav a:hover {
  background-color: #3465A4; 
}

/* Style spécifique lorsque l'élément est actif */
.topnav a.active {
  background-color: #3465A4;  /* Fond bleu pour l'élément actif */
  border: 1px solid #3465A4;  /* Garde la bordure bleue */
}
</style>
