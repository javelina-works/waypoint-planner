<template>
    <div>
      <h1>Upload GeoTIFF</h1>
      <input type="file" @change="uploadFile" />
      <p v-if="tileUrl">Tile URL: {{ tileUrl }}</p>
      <div id="map"></div>
    </div>
  </template>
  
  <script>
  import L from "leaflet";
  
  export default {
    data() {
      return {
        tileUrl: null,
        map: null,
      };
    },
    mounted() {
      // Initialize the map
      this.map = L.map("map", {
        // crs: L.CRS.EPSG4326,
      }).setView([0, 0], 2);

      // Add a tile layer placeholder
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(this.map);
    },
    methods: {
      async uploadFile(event) {
        const file = event.target.files[0];
        if (!file) return;
  
        const formData = new FormData();
        formData.append("file", file);
  
        // Send file to the backend
        const response = await fetch("http://localhost:8000/api/v1/upload", {
          method: "POST",
          body: formData,
          headers: {
            "Accept": "application/json", // Ensure the backend can handle JSON responses
            },
            credentials: "include", // Include cookies or credentials if needed
        });
  
        const data = await response.json();
        console.log(data);

        this.tileUrl = `http://localhost:8000/api/v1/tiles/CDB1GlobalGrid`;
        // this.tileUrl = `http://localhost:8000/api/v1/tiles`;
        const query_params = `?url=${data.file_url}`

        // Add the COG tile layer to the map
        L.tileLayer(`${this.tileUrl}/{z}/{x}/{y}.png${query_params}`, {
          tileSize: 256,
          maxZoom: 22,
          crs: L.CRS.EPSG4326,
        }).addTo(this.map);

        // Update the map view to focus on the bounds
        const image_endpoint = `http://localhost:8000/api/v1/bounds?url=${data.file_url}`
        await fetch(image_endpoint)
        .then(response => response.json())
        .then(data => {
            const bounds = [[data.bounds[1], data.bounds[0]], [data.bounds[3], data.bounds[2]]];
            this.map.fitBounds(bounds); // Zoom and center map on bounds
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
  