<!-- <script setup lang="ts">
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
</style> -->


<!-- <script setup lang="ts">
import { defineProps, ref } from 'vue';

const emit = defineEmits<{
  (event: 'filterCyclones', filterType: string): void;
}>();

const activeMode = ref<string>('now'); // Mode actif par défaut
const selectedDate = ref<string>('');

function setActiveMode(mode: string) {
  activeMode.value = mode;
  if (mode === 'others') {
    selectedDate.value = '';
  } else {
    emit('filterCyclones', mode);
  }
}

function handleDateChange(event: Event) {
  const target = event.target as HTMLInputElement;
  selectedDate.value = target.value;
  emit('filterCyclones', selectedDate.value);
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
      <input
        v-if="activeMode === 'others'"
        type="date"
        v-model="selectedDate"
        @change="handleDateChange"
      />
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

.topnav a.active {
  background-color: #3465A4;
  border: 1px solid #3465A4;
}

.topnav input[type="date"] {
  padding: 0.5rem;
  border: 1px solid #5e4dcd;
  border-radius: 6px;
  background-color: transparent;
  color: #fff;
  font-size: 1.2rem;
}
</style> -->


<script setup lang="ts">
import { ref, computed } from 'vue';

// Événements que ce composant émet
const emit = defineEmits<{
  (event: 'filterCyclones', filterType: string): void;
  (event: 'selectDate', date: string): void;
}>();

// Valeur courante du mode (par défaut: "now")
const activeMode = ref<string>('now');

// Date choisie pour le mode 'others'
const selectedDate = ref<string>(''); // type "YYYY-MM-DD" (string)

// Déclenché quand on clique sur l’un des boutons
function setActiveMode(mode: string) {
  activeMode.value = mode;
  emit('filterCyclones', mode);
}

// Déclenché quand on change la date dans le <input type="date">
function onDateChange(event: Event) {
  const target = event.target as HTMLInputElement;
  selectedDate.value = target.value; 
  // On émet un event "selectDate" pour informer le parent
  emit('selectDate', selectedDate.value);
}
</script>

<template>
  <div class="nav-container">
    <div class="topnav">
      <a 
        :class="{ active: activeMode === 'now' }"
        @click="setActiveMode('now')"
      >
        Temps réel
      </a>
      <a 
        :class="{ active: activeMode === 'today' }"
        @click="setActiveMode('today')"
      >
        Aujourd'hui
      </a>
      <a 
        :class="{ active: activeMode === 'others' }"
        @click="setActiveMode('others')"
      >
        Autres
      </a>

      <!-- On affiche le input de date seulement si le mode = "others" -->
      <input 
        v-if="activeMode === 'others'"
        type="date" 
        :value="selectedDate" 
        @change="onDateChange"
      />
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

.topnav a.active {
  background-color: #3465A4;
  border: 1px solid #3465A4;
}

.topnav input[type="date"] {
  color: #fff;
  background-color: #333; 
  border: 1px solid #5e4dcd; 
  border-radius: 6px;
  padding: 0.5rem;
}
</style>
