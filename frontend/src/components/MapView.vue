<template>
  <div id="map"></div>
</template>

<script>
import L from "leaflet";

export default {
  name: "MapView",
  props: ["waypoints"],
  mounted() {
    // Initialize map
    this.map = L.map("map").setView([0, 0], 2);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap contributors",
    }).addTo(this.map);

    // Add markers for waypoints
    this.waypoints.forEach((wp) => {
      L.marker([wp.lat, wp.lng]).addTo(this.map);
    });
  },
  watch: {
    // Watch for changes to waypoints and update map markers
    waypoints: {
      handler(newWaypoints) {
        newWaypoints.forEach((wp) => {
          L.marker([wp.lat, wp.lng]).addTo(this.map);
        });
      },
      deep: true,
    },
  },
};
</script>

<style>
#map {
  width: 100%;
  height: 500px;
}
</style>
