import L from 'leaflet';

// Just an example: Set up a simple map
// Make sure you have a div with id="map" in index.html
document.addEventListener('DOMContentLoaded', () => {
  const map = L.map('map').setView([40, -100], 4);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 22,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
});
