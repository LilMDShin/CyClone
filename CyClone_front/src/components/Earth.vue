<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

const globeContainer = ref<HTMLDivElement | null>(null);
// const currentName = ref('');
// const newName = ref('');
let viewer: Cesium.Viewer | null = null;
let ws: WebSocket | null = null;
const WS_URL = 'ws://localhost:8765';
// const API_URL = 'http://localhost:8111'; // URL de votre API
const activeCyclones = ref<Map<string, Cesium.Entity>>(new Map());
const cycloneLastUpdate = new Map<string, number>();

const MAX_INACTIVITY_DURATION = 1000;

onMounted(() => {
  if (globeContainer.value) {
    viewer = new Cesium.Viewer(globeContainer.value, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      sceneModePicker: false,
    });
  }

  connectWebSocket();
  setInterval(checkCycloneActivity, 1000);
});

onUnmounted(() => {
  if (ws) {
    ws.close();
    ws = null;
  }
  if (viewer) {
    viewer.destroy();
  }
});

function connectWebSocket() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    console.log('WebSocket connecté.');
  };

  ws.onmessage = (event) => {
    console.log('Message WebSocket reçu brut:', event.data);

    try {
      const cycloneData = JSON.parse(event.data);
      console.log('Cyclone reçu:', cycloneData);
      displayCyclone(cycloneData);
    } catch (error) {
      console.error('Erreur lors du parsing du message WebSocket :', error);
    }
  };

  ws.onerror = (error) => {
    console.error('Erreur WebSocket :', error);
  };

  ws.onclose = (event) => {
    console.log(`WebSocket déconnecté. Code : ${event.code}, Raison : ${event.reason}`);
    setTimeout(connectWebSocket, 5000);
  };
}

async function updateDissipationDate(cycloneName: string, dissipationDate: string) {
  try {
    const response = await fetch(`http://0.0.0.0:8111/cyclones/${encodeURIComponent(cycloneName)}/dissipationdate`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ dissipationdate: dissipationDate }),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error(`Erreur lors de la mise à jour de la date de dissipation pour ${cycloneName}:`, error.detail);
    } else {
      console.log(`Date de dissipation mise à jour pour ${cycloneName}: ${dissipationDate}`);
    }
  } catch (error) {
    console.error(`Erreur lors de la requête de mise à jour de la date de dissipation pour ${cycloneName}:`, error);
  }
}

function checkCycloneActivity() {
  const now = Date.now();

  for (const [cycloneName, lastUpdate] of cycloneLastUpdate.entries()) {
    if (now - lastUpdate > MAX_INACTIVITY_DURATION) {
      const entity = activeCyclones.value.get(cycloneName);
      if (entity && viewer) {
        viewer.entities.remove(entity);
      }
      activeCyclones.value.delete(cycloneName);
      cycloneLastUpdate.delete(cycloneName);
      console.log(`Cyclone ${cycloneName} supprimé pour cause d'inactivité.`);

      // Ajouter dissipation date dans la BDD
      const dissipationDate = new Date().toISOString();
      updateDissipationDate(cycloneName, dissipationDate);
    }
  }
}


async function displayCyclone(cycloneData: any) {
  if (!viewer) return;

  const cycloneName = cycloneData.cyclone_name;

  // Mettre à jour le dernier timestamp pour le cyclone
  cycloneLastUpdate.set(cycloneName, Date.now());

  // Supprimer les anciennes entités si elles existent
  if (activeCyclones.value.has(cycloneName)) {
    const existingEntity = activeCyclones.value.get(cycloneName);
    if (existingEntity) {
      viewer.entities.remove(existingEntity);
    }
  }

  // Ajouter une entité pour la position actuelle
  const position = Cesium.Cartesian3.fromDegrees(cycloneData.longitude, cycloneData.latitude);
  const currentEntity = viewer.entities.add({
    position: position,
    billboard: {
      image: '/src/assets/hurricane2.png',
      width: 50,
      height: 50,
    },
    label: {
      text: `${cycloneName}
Intensity: ${cycloneData.intensity}
Lat: ${cycloneData.latitude.toFixed(2)}°
Lon: ${cycloneData.longitude.toFixed(2)}°`,
      font: '14pt sans-serif',
      pixelOffset: new Cesium.Cartesian2(0, -70),
      showBackground: true,
      backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
      fillColor: Cesium.Color.WHITE,
    },
  });

  activeCyclones.value.set(cycloneName, currentEntity);

  // Requête pour récupérer toute la trajectoire
  try {
    const response = await fetch(`http://0.0.0.0:8111/cyclones/${encodeURIComponent(cycloneName)}`);
    if (!response.ok) {
      console.error(`Erreur lors de la récupération des données pour ${cycloneName}:`, response.statusText);
      return;
    }

    const fullCycloneData = await response.json();

    // Supprimer toute trajectoire précédente si elle existe
    viewer.entities.removeById(`trajectory-${cycloneName}`);

    // Ajouter la trajectoire
    const positions = fullCycloneData.observations.map((obs: any) =>
      Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude)
    );

    viewer.entities.add({
      id: `trajectory-${cycloneName}`,
      polyline: {
        positions: positions,
        width: 3,
        material: Cesium.Color.RED,
        clampToGround: true, // Colle la ligne au sol
      },
    });
  } catch (error) {
    console.error(`Erreur lors de la récupération des données pour ${cycloneName}:`, error);
  }
}

/*
async function renameCyclone() {
  if (!currentName.value || !newName.value) {
    alert('Veuillez entrer les noms actuel et nouveau du cyclone.');
    return;
  }

  try {
    const response = await fetch(`${API_URL}/cyclones/${encodeURIComponent(currentName.value)}/rename?new_name=${encodeURIComponent(newName.value)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      const error = await response.json();
      alert(`Erreur lors du renommage : ${error.detail}`);
      return;
    }

    const updatedCyclone = await response.json();
    console.log(`Cyclone renommé : ${updatedCyclone.name}`);

    // Update display
    if (activeCyclones.value.has(currentName.value)) {
      const entity = activeCyclones.value.get(currentName.value);
      if (entity) {
        viewer?.entities.remove(entity);
        activeCyclones.value.delete(currentName.value);
        cycloneLastUpdate.delete(currentName.value);
      }
    }

    currentName.value = '';
    newName.value = '';
    alert(`Cyclone renommé avec succès en ${newName.value}`);
  } catch (error) {
    console.error('Erreur lors du renommage du cyclone :', error);
    alert('Une erreur est survenue lors du renommage.');
  }
}
*/
</script>

<template>
  <div>
    <div ref="globeContainer" class="globe-container"></div>
    <div class="nav-container">
      <!--
      <div class="topnav">
        <input type="text" v-model="currentName" placeholder="Nom actuel" />
        <input type="text" v-model="newName" placeholder="Nouveau nom" />
        <a href="#" @click.prevent="renameCyclone">Renommer le cyclone</a>
      </div>
      -->
    </div>
  </div>
</template>

<style scoped>
.globe-container {
  width: 100%;
  height: 80vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

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
  gap: 1rem;
} 

.topnav input {
  color: #fff;
  background-color: #333; 
  border: 1px solid #5e4dcd; 
  border-radius: 6px;
  padding: 0.5rem;
}

.topnav a {
  color: #fff; 
  text-decoration: none; 
  padding: 0.5rem 1rem; 
  border: 1px solid #5e4dcd; 
  border-radius: 6px; 
  background-color: transparent;
  font-size: 1rem; 
  transition: background-color 0.3s ease; 
}

.topnav a:hover {
  background-color: #3465A4; 
}

.topnav a.active {
  background-color: #3465A4;
  border: 1px solid #3465A4;
}
</style>

