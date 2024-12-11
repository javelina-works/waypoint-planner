<template>
    <div id="map"></div>
</template>
  
  <script>
  import L from "leaflet";
  
  export default {
    props: ["waypoints"],
    data() {
      return {
        map: null,
        waypointMarkers: {},
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
        updateMarkers() {
            const currentIndices = Object.keys(this.waypointMarkers).map(Number);

            // Add or update markers based on waypoints
            this.waypoints.forEach((wp, index) => {
                if (this.waypointMarkers[index]) {
                    // Update marker position if it already exists
                    this.waypointMarkers[index].setLatLng([wp.lat, wp.lng]);
                } else {
                    // Create a new marker if it doesn't exist
                    const marker = L.marker([wp.lat, wp.lng], { draggable: true });
                    // marker.bindTooltip(`Waypoint ${index + 1}`).openTooltip();
                    marker.addTo(this.map);

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
  