<template>
  <h3>Upload GeoTIFF</h3>
  <input type="file" @change="uploadFile" />
  <p v-if="tileUrl">Tile URL: {{ tileUrl }}</p>
  <div id="map"></div>
</template>

<script>
import L from "leaflet";

// Disable tooltip animations globally
L.Marker.prototype.options.autoPan = false; // Prevent auto-panning on tooltip open
L.Tooltip.prototype.options.interactive = false; // Disable tooltip interactivity
// L.Tooltip.prototype.options.permanent = true; // Make tooltips always visible (optional)



export default {
  name: 'Waypoint Planner',
  props: ["waypoints"],
  data() {
    return {
      map: null,
      waypointMarkers: {},
      tileUrl: null,
    };
  },
  mounted() {
    // Initialize the map
    this.map = L.map("map").setView([0, 0], 2);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors',
    }).addTo(this.map);

    // Handle map click to add waypoints
    this.map.on("click", (e) => {
      const latLng = e.latlng;
      this.$emit("add-waypoint", latLng); // Emit event to parent
    });

    // Watch for waypoint updates and redraw markers
    this.updateMarkers();
  },
  watch: {
    waypoints: {
      deep: true,
      handler() {
        this.updateMarkers();
      },
    },
  },
  methods: {
    async uploadFile(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      // Send file to the backend
      const response = await fetch("http://localhost:80/api/v1/upload", {
        method: "POST",
        body: formData,
        headers: {
          "Accept": "application/json", // Ensure the backend can handle JSON responses
        },
        credentials: "include", // Include cookies or credentials if needed
      });

      const data = await response.json();
      console.log(data);

      this.tileUrl = `http://localhost:80/api/v1/tiles/WebMercatorQuad`;
      // this.tileUrl = `http://localhost:8000/api/v1/tiles`;
      const query_params = `?url=${data.file_url}`

      // Add the COG tile layer to the map
      L.tileLayer(`${this.tileUrl}/{z}/{x}/{y}.png${query_params}`, {
        tileSize: 256,
        maxZoom: 22,
        crs: L.CRS.EPSG4326,
      }).addTo(this.map);

      // Update the map view to focus on the bounds
      const image_endpoint = `http://localhost:80/api/v1/bounds?url=${data.file_url}`
      await fetch(image_endpoint)
        .then(response => response.json())
        .then(data => {
          const bounds = [[data.bounds[1], data.bounds[0]], [data.bounds[3], data.bounds[2]]];
          this.map.fitBounds(bounds); // Zoom and center map on bounds
        });

    },

    updateMarkers() {
      const currentIndices = Object.keys(this.waypointMarkers).map(Number);

      // Add or update markers based on waypoints
      this.waypoints.forEach((wp, index) => {
        if (this.waypointMarkers[index]) {
          // Update marker position if it already exists
          const marker = this.waypointMarkers[index];
          marker.setLatLng([wp.lat, wp.lng]);
        } else {
          // Create a new marker if it doesn't exist
          const marker = L.marker([wp.lat, wp.lng], { draggable: true, title: `Waypoint ${index + 1}` });
          marker.addTo(this.map);
          // marker.bindTooltip(`${index + 1}`, { permanent: true, direction: 'top' }).openTooltip();

          // Handle dragend to emit updates
          marker.on("dragend", () => {
            const newLatLng = marker.getLatLng();
            console.log("Drag ended for marker at index:", index, newLatLng);
            this.$emit("update-waypoint", { index, latLng: newLatLng });
            this.waypointMarkers[index].setLatLng(newLatLng);
          });
          this.waypointMarkers[index] = marker; // Store the marker reference
        }
      });

      // Remove stale markers
      currentIndices.forEach((index) => {
        if (!this.waypoints[index]) {
          this.map.removeLayer(this.waypointMarkers[index]);
          delete this.waypointMarkers[index];
        }
      });
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