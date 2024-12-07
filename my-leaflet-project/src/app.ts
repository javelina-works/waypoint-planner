import L, { LatLng } from "leaflet";
import "leaflet-draw";

interface MarkerCoord {
  lat: number;
  lng: number;
}

// Initialize the map
const map = L.map('map').setView([40, -100], 4);

// Add a base tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 22,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// FeatureGroup to store drawn items
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Draw control
const drawControl = new L.Control.Draw({
  draw: {
    // marker: true,
    polygon: false,
    polyline: false,
    rectangle: false,
    circle: false,
    circlemarker: false
  },
  edit: {
    featureGroup: drawnItems,
    // edit: true,
    remove: true
  }
});
map.addControl(drawControl);

let markers: MarkerCoord[] = [];

function updateWaypointTable() {
  const tbody = document.querySelector('#waypoint-list tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  markers.forEach((m, i) => {
    const row = document.createElement('tr');
    const idxCell = document.createElement('td');
    idxCell.textContent = (i + 1).toString();
    const latCell = document.createElement('td');
    latCell.textContent = m.lat.toFixed(6);
    const lngCell = document.createElement('td');
    lngCell.textContent = m.lng.toFixed(6);
    row.appendChild(idxCell);
    row.appendChild(latCell);
    row.appendChild(lngCell);
    tbody.appendChild(row);
  });
}

map.on(L.Draw.Event.CREATED, (evt: L.LeafletEvent) => {
  const e = evt as L.DrawEvents.Created;
  const layer = e.layer;
  drawnItems.addLayer(layer);
  if (layer instanceof L.Marker) {
    const latlng: LatLng = layer.getLatLng();
    markers.push({ lat: latlng.lat, lng: latlng.lng });
    updateWaypointTable();
  }
});

map.on(L.Draw.Event.DELETED, (evt: L.LeafletEvent) => {
  const e = evt as L.DrawEvents.Deleted;
  const layers = e.layers;
  layers.eachLayer(layer => {
    if (layer instanceof L.Marker) {
      const latlng = layer.getLatLng();
      markers = markers.filter(m => !(Math.abs(m.lat - latlng.lat) < 1e-12 && Math.abs(m.lng - latlng.lng) < 1e-12));
    }
  });
  updateWaypointTable();
});

map.on(L.Draw.Event.EDITED, (evt: L.LeafletEvent) => {
    const e = evt as L.DrawEvents.Edited;
  // Rebuild markers from drawnItems
  markers = [];
  drawnItems.eachLayer(layer => {
    if (layer instanceof L.Marker) {
      const latlng = layer.getLatLng();
      markers.push({ lat: latlng.lat, lng: latlng.lng });
    }
  });
  updateWaypointTable();
});
