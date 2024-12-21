<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css'; 

const globeContainer = ref<HTMLDivElement | null>(null);


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
</style>
