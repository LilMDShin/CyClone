<!-- <script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css'; 

const globeContainer = ref<HTMLDivElement | null>(null);
const cycloneEntities = ref<Map<number, Cesium.Entity>>(new Map());
const props = defineProps<{ filter: string }>();

onMounted(async () => {
  if (globeContainer.value) {
    const viewer = new Cesium.Viewer(globeContainer.value, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      sceneModePicker: false,
    });

    // Charger les données initiales
    await updateCyclones(props.filter);

    // Observer les changements de "filter"
    watch(
      () => props.filter,
      async (newFilter, oldFilter) => {
        console.log(`Filter changed from ${oldFilter} to ${newFilter}`);
        // Mettre à jour les cyclones en fonction du nouveau filtre
        await updateCyclones(newFilter);
      }
    );

    async function updateCyclones(filter: string) {
      const response = await fetch('./src/coord.json');
      const cycloneData = await response.json();

      const today = new Date().toISOString().split('T')[0];

      // Filtrer les cyclones en fonction du filtre
      const filteredCyclones = filter === 'today'
        ? cycloneData.cyclones.filter((cyclone: any) =>
            cyclone.observations.some((obs: any) =>
              obs.observationDate.startsWith(today)
            )
          )
        : cycloneData.cyclones;

      // Effacer toutes les entités existantes
      viewer.entities.removeAll();

      // Ajouter les cyclones filtrés
      filteredCyclones.forEach((cyclone: any) => {
        const positions: Cesium.Cartesian3[] = [];

        cyclone.observations.forEach((obs: any, index: number) => {
          positions.push(Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude));

          if (index === cyclone.observations.length - 1) {
            viewer.entities.add({
              position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
              billboard: {
                image: "./src/assets/hurricane2.png",
                width: 50,
                height: 50,
                scale: obs.observationRadius / 100,
              },
              label: {
                text: `${cyclone.name}\nIntensity: ${obs.intensity}`,
                font: "14pt sans-serif",
                pixelOffset: new Cesium.Cartesian2(0, -50),
                showBackground: true,
                backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
                fillColor: Cesium.Color.WHITE,
              },
            });
          }
        });

        if (positions.length > 1) {
          viewer.entities.add({
            polyline: {
              positions: positions,
              width: 3,
              material: Cesium.Color.RED,
            },
          });
        }
      });

      // viewer.zoomTo(viewer.entities);
    }
  }
});
</script>

<template>
  <div ref="globeContainer" class="globe-container"></div>
</template>

<style scoped>
.globe-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
</style> -->

<!-- <script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

const globeContainer = ref<HTMLDivElement | null>(null);
const cycloneEntities = ref<Map<number, Cesium.Entity>>(new Map()); // Stocker les entités par id_device
const props = defineProps<{ filter: string }>();

onMounted(() => {
  let viewer: Cesium.Viewer | null = null;
  let websocket: WebSocket | null = null;

  if (globeContainer.value) {
    viewer = new Cesium.Viewer(globeContainer.value, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      sceneModePicker: false,
    });

    // Observer les changements de "filter"
    watch(
      () => props.filter,
      (newFilter, oldFilter) => {
        console.log(`Filter changed from ${oldFilter} to ${newFilter}`);
        if (newFilter === "now") {
          connectWebSocket();
        } else {
          disconnectWebSocket();
          // Charger les données statiques si nécessaire
          loadStaticCyclones(viewer!, newFilter);
        }
      }
    );

    // Charger les données initiales
    if (props.filter !== "now") {
      loadStaticCyclones(viewer, props.filter);
    } else {
      connectWebSocket();
    }
  }

  // Fonction pour charger les cyclones statiques
  async function loadStaticCyclones(viewer: Cesium.Viewer, filter: string) {
    const response = await fetch('./src/coord.json');
    const cycloneData = await response.json();

    const today = new Date().toISOString().split('T')[0];
    const filteredCyclones = filter === "today"
      ? cycloneData.cyclones.filter((cyclone: any) =>
          cyclone.observations.some((obs: any) =>
            obs.observationDate.startsWith(today)
          )
        )
      : cycloneData.cyclones;

    viewer.entities.removeAll();
    cycloneEntities.value.clear();

    filteredCyclones.forEach((cyclone: any) => {
      cyclone.observations.forEach((obs: any, index: number) => {
        if (index === cyclone.observations.length - 1) {
          const entity = viewer.entities.add({
            position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
            billboard: {
              image: "./src/assets/hurricane2.png",
              width: 50,
              height: 50,
              scale: obs.observationRadius / 100,
            },
            label: {
              text: `${cyclone.name}\nIntensity: ${obs.intensity}`,
              font: "14pt sans-serif",
              pixelOffset: new Cesium.Cartesian2(0, -50),
              showBackground: true,
              backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
              fillColor: Cesium.Color.WHITE,
            },
          });
          cycloneEntities.value.set(cyclone.id, entity);
        }
      });
    });
  }

  // Connexion au WebSocket
  function connectWebSocket() {
    if (websocket) return; // Éviter plusieurs connexions

    websocket = new WebSocket('ws://localhost:8765');

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      updateCyclonePosition(message);
    };

    websocket.onclose = () => {
      console.log("WebSocket disconnected");
      websocket = null;
    };
  }

  // Déconnexion du WebSocket
  function disconnectWebSocket() {
    if (websocket) {
      websocket.close();
      websocket = null;
    }
  }

  // Mise à jour de la position des cyclones en temps réel
  function updateCyclonePosition(data: { id_device: number; latitude: number; longitude: number; date: string }) {
    const viewerEntity = cycloneEntities.value.get(data.id_device);

    if (viewerEntity) {
      // Mettre à jour la position de l'entité existante
      viewerEntity.position = Cesium.Cartesian3.fromDegrees(data.longitude, data.latitude);
    } else if (viewer) {
      // Ajouter une nouvelle entité pour un nouveau cyclone
      const newEntity = viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(data.longitude, data.latitude),
        billboard: {
          image: "./src/assets/hurricane2.png",
          width: 50,
          height: 50,
        },
      });
      cycloneEntities.value.set(data.id_device, newEntity);
    }
  }
});
</script> -->

<!-- <script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

const globeContainer = ref<HTMLDivElement | null>(null);
const cycloneEntities = ref<Map<number, Cesium.Entity>>(new Map());
const props = defineProps<{ filter: string }>();

let websocket: WebSocket | null = null;

onMounted(async () => {
  if (globeContainer.value) {
    const viewer = new Cesium.Viewer(globeContainer.value, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      sceneModePicker: false,
    });

    const updateCyclones = async (filter: string) => {
      if (filter === 'now') {
        // Connect to WebSocket for real-time updates
        if (!websocket) {
          websocket = new WebSocket('ws://127.0.0.1:8765/');
          websocket.onmessage = (event) => {
            const cycloneData = JSON.parse(event.data);
            updateRealTimeCyclones(cycloneData);
          };
        }
      } else {
        // Disconnect WebSocket if not in "now" mode
        if (websocket) {
          websocket.close();
          websocket = null;
        }

        // Load and display static cyclone data
        const response = await fetch('./src/coord.json');
        const cycloneData = await response.json();
        displayCyclones(cycloneData.cyclones, filter);
      }
    };

    const displayCyclones = (cyclones: any[], filter: string) => {
      viewer.entities.removeAll();
      cyclones.forEach((cyclone) => {
        cyclone.observations.forEach((obs: any, index: number) => {
        if (index === cyclone.observations.length - 1) {
          const entity = viewer.entities.add({
            position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
            billboard: {
              image: "./src/assets/hurricane2.png",
              width: 50,
              height: 50,
              scale: obs.observationRadius / 100,
            },
            label: {
              text: `${cyclone.name}\nIntensity: ${obs.intensity}`,
              font: "14pt sans-serif",
              pixelOffset: new Cesium.Cartesian2(0, -50),
              showBackground: true,
              backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
              fillColor: Cesium.Color.WHITE,
            },
          });
          cycloneEntities.value.set(cyclone.id, entity);
        }
      });
      });
    };

    const updateRealTimeCyclones = (cycloneData: any) => {
      // Logic to update real-time cyclone data
      viewer.entities.removeAll();
      const positions: Cesium.Cartesian3[] = [];
      cycloneData.observations.forEach((obs: any, index: number) => {
        positions.push(Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude));
        if (index === cycloneData.observations.length - 1) {
          viewer.entities.add({
            position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
            billboard: {
              image: './src/assets/hurricane2.png',
              width: 50,
              height: 50,
              scale: obs.observationRadius / 100,
            },
            label: {
              text: `${cycloneData.name}\nIntensity: ${obs.intensity}`,
              font: '14pt sans-serif',
              pixelOffset: new Cesium.Cartesian2(0, -50),
              showBackground: true,
              backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
              fillColor: Cesium.Color.WHITE,
            },
          });
        }
      });

      if (positions.length > 1) {
        viewer.entities.add({
          polyline: {
            positions: positions,
            width: 3,
            material: Cesium.Color.RED,
          },
        });
      }
    };

    watch(() => props.filter, updateCyclones);

    // Initial load
    await updateCyclones(props.filter);

    onUnmounted(() => {
      if (websocket) {
        websocket.close();
      }
    });
  }
});
</script>

<template>
  <div ref="globeContainer" class="globe-container"></div>
</template>

<style scoped>
.globe-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
</style> -->


<!-- <script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

const globeContainer = ref<HTMLDivElement | null>(null);
const cycloneEntities = ref<Map<number, Cesium.Entity>>(new Map());
const props = defineProps<{ filter: string }>();

let websocket: WebSocket | null = null;
let viewer: Cesium.Viewer | null = null;

onMounted(async () => {
  if (globeContainer.value) {
    viewer = new Cesium.Viewer(globeContainer.value, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      sceneModePicker: false,
    });

    const updateCyclones = async (filter: string) => {
      if (filter === 'now') {
        // Connect to WebSocket for real-time updates
        if (!websocket) {
          websocket = new WebSocket('ws://127.0.0.1:8765/events');
          websocket.onmessage = (event) => {
            const cycloneData = JSON.parse(event.data);
            updateRealTimeCyclones(cycloneData);
          };
        }
      } else {
        // Disconnect WebSocket if not in "now" mode
        if (websocket) {
          websocket.close();
          websocket = null;
        }

        // Load and display static cyclone data
        const response = await fetch(`http://localhost:8000/cyclones/${filter === 'today' ? new Date().toISOString().split('T')[0] : filter}`);
        const cycloneData = await response.json();
        displayCyclones(cycloneData.cyclones, filter);
      }
    };

    const displayCyclones = (cyclones: any[], filter: string) => {
      viewer?.entities.removeAll();
      cyclones.forEach((cyclone) => {
        cyclone.observations.forEach((obs: any, index: number) => {
          if (index === cyclone.observations.length - 1) {
            const entity = viewer?.entities.add({
              position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
              billboard: {
                image: "./src/assets/hurricane2.png",
                width: 50,
                height: 50,
                scale: obs.observationRadius / 100,
              },
              label: {
                text: `${cyclone.name}\nIntensity: ${obs.intensity}`,
                font: "14pt sans-serif",
                pixelOffset: new Cesium.Cartesian2(0, -50),
                showBackground: true,
                backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
                fillColor: Cesium.Color.WHITE,
              },
            });
            cycloneEntities.value.set(cyclone.id, entity);
          }
        });
      });
    };

    const updateRealTimeCyclones = (cycloneData: any) => {
      // Logic to update real-time cyclone data
      viewer?.entities.removeAll();
      const positions: Cesium.Cartesian3[] = [];
      cycloneData.observations.forEach((obs: any, index: number) => {
        positions.push(Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude));
        if (index === cycloneData.observations.length - 1) {
          viewer?.entities.add({
            position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
            billboard: {
              image: './src/assets/hurricane2.png',
              width: 50,
              height: 50,
              scale: obs.observationRadius / 100,
            },
            label: {
              text: `${cycloneData.name}\nIntensity: ${obs.intensity}`,
              font: '14pt sans-serif',
              pixelOffset: new Cesium.Cartesian2(0, -50),
              showBackground: true,
              backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
              fillColor: Cesium.Color.WHITE,
            },
          });
        }
      });

      if (positions.length > 1) {
        viewer?.entities.add({
          polyline: {
            positions: positions,
            width: 3,
            material: Cesium.Color.RED,
          },
        });
      }
    };

    watch(() => props.filter, updateCyclones);

    // Initial load
    await updateCyclones(props.filter);

    onUnmounted(() => {
      if (websocket) {
        websocket.close();
      }
    });
  }
});
</script>

<template>
  <div ref="globeContainer" class="globe-container"></div>
</template>

<style scoped>
.globe-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
</style> -->


<!-- <script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

// Props : on reçoit "filter" et, si on veut, "selectedDate"
const props = defineProps<{
  filter: string;
  selectedDate?: string; // date "YYYY-MM-DD" en mode others
}>();

// Références pour le DOM et la map
const globeContainer = ref<HTMLDivElement | null>(null);
let viewer: Cesium.Viewer | null = null;

// SSE
let eventSource: EventSource | null = null;

// On stocke ici un "Map" pour associer un cycloneId à une entity Cesium
const cycloneEntities = ref<Map<number, Cesium.Entity>>(new Map());

// === LIFECYCLE ===
onMounted(() => {
  if (globeContainer.value) {
    // Initialisation du viewer Cesium
    viewer = new Cesium.Viewer(globeContainer.value, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      sceneModePicker: false,
    });
  }

  // On écoute toute modification de props.filter
  watch(
    () => props.filter,
    (newFilter) => {
      updateCyclones(newFilter, props.selectedDate);
    },
    { immediate: true }
  );

  // On écoute aussi les modifications de selectedDate si filter = 'others'
  watch(
    () => props.selectedDate,
    (newDate) => {
      if (props.filter === 'others' && newDate) {
        updateCyclones('others', newDate);
      }
    }
  );
});

// Quand le composant se démonte, on ferme la connexion SSE si elle est ouverte
onUnmounted(() => {
  if (eventSource) {
    eventSource.close();
  }
  if (viewer) {
    viewer.destroy();
  }
});

// === FONCTIONS PRINCIPALES ===

// Cette fonction principale est appelée dès que filter (ou date) change
async function updateCyclones(filter: string, date?: string) {
  // Si on n’a pas de viewer, on ne fait rien
  if (!viewer) return;

  // On efface les entités déjà affichées
  viewer.entities.removeAll();

  // 1) Mode temps réel => ouverture SSE
  if (filter === 'now') {
    // On ferme d’abord un éventuel EventSource existant
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    // On ouvre la connexion SSE
    eventSource = new EventSource('http://localhost:8765/events');
    eventSource.onmessage = (event) => {
      // event.data contient la string envoyée par SSE
      // c’est un objet JSON => on le parse
      const cycloneData = JSON.parse(event.data);
      updateRealTimeCyclones(cycloneData);
    };
    eventSource.onerror = (err) => {
      console.error('SSE error:', err);
    };
  } 

  // 2) Mode "today" => on fetch l’API du back, ex: /cyclones/<AUJOURDHUI>
  else if (filter === 'today') {
    // On ferme SSE s’il existait
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    // Suppose qu’on génère la date du jour en "YYYY-MM-DD"
    const today = new Date().toISOString().split('T')[0]; 
    const url = `http://localhost:8000/cyclones/${today}`;
    // On fetch
    const response = await fetch(url);
    const data = await response.json();
    // data est un tableau de cyclones
    // On les affiche
    displayCyclones(data);
  }

  // 3) Mode "others" => date choisie par l’utilisateur
  else if (filter === 'others' && date) {
    // On ferme SSE s’il existait
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    // On fetch /cyclones/<DATE>
    const url = `http://localhost:8000/cyclones/${date}`;
    const response = await fetch(url);
    const data = await response.json();
    displayCyclones(data);
  }
}

// Affichage de cyclones "statiques" (liste)
function displayCyclones(cyclones: any[]) {
  if (!viewer) return;
  // On parcourt chaque cyclone
  cyclones.forEach((cyclone: any) => {
    // Il vous faudra peut-être, selon votre structure BDD,
    // récupérer la liste d'observations autrement
    // Dans votre code, "cyclone.observations" contient les points du cyclone
    if (!cyclone.observations) return;

    // On trace un polyline (la trajectoire)
    const positions: Cesium.Cartesian3[] = cyclone.observations.map((obs: any) =>
      Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude)
    );

    // On ajoute la dernière observation comme billboard
    const lastObs = cyclone.observations[cyclone.observations.length - 1];
    const entity = viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(lastObs.longitude, lastObs.latitude),
      billboard: {
        image: './src/assets/hurricane2.png',
        width: 50,
        height: 50,
        scale: lastObs.observationRadius ? (lastObs.observationRadius / 100) : 0.5,
      },
      label: {
        text: `${cyclone.name}\nIntensity: ${lastObs.intensity}`,
        font: '14pt sans-serif',
        pixelOffset: new Cesium.Cartesian2(0, -50),
        showBackground: true,
        backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
        fillColor: Cesium.Color.WHITE,
      },
    });

    cycloneEntities.value.set(cyclone.id, entity);

    // On ajoute le polyline
    if (positions.length > 1) {
      viewer.entities.add({
        polyline: {
          positions: positions,
          width: 3,
          material: Cesium.Color.RED,
        },
      });
    }
  });
}

// Mise à jour "temps réel" - un seul cycloneData reçu via SSE
function updateRealTimeCyclones(cycloneData: any) {
  if (!viewer) return;
  viewer.entities.removeAll();

  // On construit le polyline depuis la liste d’observations
  const positions: Cesium.Cartesian3[] = [];
  cycloneData.observations.forEach((obs: any, index: number) => {
    positions.push(Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude));
    // On affiche le dernier point avec une icône
    if (index === cycloneData.observations.length - 1) {
      viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude),
        billboard: {
          image: './src/assets/hurricane2.png',
          width: 50,
          height: 50,
          scale: obs.observationRadius ? (obs.observationRadius / 100) : 0.5,
        },
        label: {
          text: `${cycloneData.name}\nIntensity: ${obs.intensity}`,
          font: '14pt sans-serif',
          pixelOffset: new Cesium.Cartesian2(0, -50),
          showBackground: true,
          backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
          fillColor: Cesium.Color.WHITE,
        },
      });
    }
  });

  // On trace le polyline
  if (positions.length > 1) {
    viewer.entities.add({
      polyline: {
        positions: positions,
        width: 3,
        material: Cesium.Color.RED,
      },
    });
  }
}
</script>

<template>
  <div ref="globeContainer" class="globe-container"></div>
</template>

<style scoped>
.globe-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
</style> -->

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

const props = defineProps<{
  filter: string;
  selectedDate?: string;
}>();

const globeContainer = ref<HTMLDivElement | null>(null);
let viewer: Cesium.Viewer | null = null;
let ws: WebSocket | null = null;
const WS_URL = 'ws://localhost:8765';
const API_URL = 'http://localhost:8000';
const cycloneEntities = ref<Map<number, Cesium.Entity>>(new Map());

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

  watch(
    () => props.filter,
    (newFilter) => {
      updateCyclones(newFilter, props.selectedDate);
    },
    { immediate: true }
  );

  watch(
    () => props.selectedDate,
    (newDate) => {
      if (props.filter === 'others' && newDate) {
        updateCyclones('others', newDate);
      }
    }
  );
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

async function updateCyclones(filter: string, date?: string) {
  if (!viewer) return;
  viewer.entities.removeAll();

  if (filter === 'now') {
    if (ws) {
      ws.close();
      ws = null;
    }

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log('WebSocket connecté.');
    };

    ws.onmessage = (event) => {
      try {
        const cycloneData = JSON.parse(event.data);
        displayRealTimeCyclone(cycloneData);
      } catch (error) {
        console.error('Erreur lors du parsing du message WebSocket :', error);
      }
    };

    ws.onerror = (error) => {
      console.error('Erreur WebSocket :', error);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket déconnecté. Code : ${event.code}, Raison : ${event.reason}`);
    };
  } else if (filter === 'today') {
    if (ws) {
      ws.close();
      ws = null;
    }

    const today = new Date().toISOString().split('T')[0];
    const url = `${API_URL}/cyclones/${today}`;

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Erreur lors du fetch des cyclones d\'aujourd\'hui.');
      const data = await response.json();
      displayCyclones(data);
    } catch (error) {
      console.error(error);
    }
  } else if (filter === 'others' && date) {
    if (ws) {
      ws.close();
      ws = null;
    }

    const url = `${API_URL}/cyclones/${date}`;

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Erreur lors du fetch des cyclones pour la date ${date}.`);
      const data = await response.json();
      displayCyclones(data);
    } catch (error) {
      console.error(error);
    }
  }
}

function displayRealTimeCyclone(cycloneData: any) {
  if (!viewer) return;
  viewer.entities.removeAll();

  const positions: Cesium.Cartesian3[] = [];

  cycloneData.observations.forEach((obs: any, index: number) => {
    const position = Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude);
    positions.push(position);

    if (index === cycloneData.observations.length - 1) {
      viewer.entities.add({
        position: position,
        billboard: {
          image: './src/assets/hurricane2.png',
          width: 50,
          height: 50,
          scale: obs.observationRadius ? obs.observationRadius / 100 : 0.5,
        },
        label: {
          text: `${cycloneData.name}\nIntensity: ${obs.intensity}`,
          font: '14pt sans-serif',
          pixelOffset: new Cesium.Cartesian2(0, -50),
          showBackground: true,
          backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
          fillColor: Cesium.Color.WHITE,
        },
      });
    }
  });

  if (positions.length > 1) {
    viewer.entities.add({
      polyline: {
        positions: positions,
        width: 3,
        material: Cesium.Color.RED,
      },
    });
  }
}

function displayCyclones(cyclones: any[]) {
  if (!viewer) return;

  cyclones.forEach((cyclone: any) => {
    if (!cyclone.observations || cyclone.observations.length === 0) return;

    const positions: Cesium.Cartesian3[] = cyclone.observations.map((obs: any) =>
      Cesium.Cartesian3.fromDegrees(obs.longitude, obs.latitude)
    );

    const lastObs = cyclone.observations[cyclone.observations.length - 1];
    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(lastObs.longitude, lastObs.latitude),
      billboard: {
        image: './src/assets/hurricane2.png',
        width: 50,
        height: 50,
        scale: lastObs.observationRadius ? lastObs.observationRadius / 100 : 0.5,
      },
      label: {
        text: `${cyclone.name}\nIntensity: ${lastObs.intensity}`,
        font: '14pt sans-serif',
        pixelOffset: new Cesium.Cartesian2(0, -50),
        showBackground: true,
        backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
        fillColor: Cesium.Color.WHITE,
      },
    });

    if (positions.length > 1) {
      viewer.entities.add({
        polyline: {
          positions: positions,
          width: 3,
          material: Cesium.Color.RED,
        },
      });
    }
  });
}
</script>

<template>
  <div ref="globeContainer" class="globe-container"></div>
</template>

<style scoped>
.globe-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
</style>