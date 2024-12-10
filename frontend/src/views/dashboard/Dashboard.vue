<script setup>

</script>

<script>
import { CCol, CRow } from '@coreui/vue';
import L from 'leaflet';

export default {
  name: 'Dashboard',
  data() {
    return {
      map: null,
      waypoints: [], // Array to store waypoints
    };
  },
  mounted() {
    // Initialize the map
    this.map = L.map('map').setView([0, 0], 2);

    // Add a tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors',
    }).addTo(this.map);

    // Add click event to add waypoints
    this.map.on('click', this.addWaypoint);
  },
  methods: {
    addWaypoint(event) {
      const { lat, lng } = event.latlng;

      // Add marker to the map
      const marker = L.marker([lat, lng], { draggable: true }).addTo(this.map);

      // Update waypoints array
      this.waypoints.push({ lat, lng, marker });

      // Update position when marker is dragged
      marker.on('dragend', () => {
        const { lat, lng } = marker.getLatLng();
        const index = this.waypoints.findIndex(wp => wp.marker === marker);
        if (index !== -1) {
          this.waypoints[index].lat = lat;
          this.waypoints[index].lng = lng;
        }
      });
    },
    removeWaypoint(index) {
      // Remove marker from map
      this.map.removeLayer(this.waypoints[index].marker);

      // Remove waypoint from array
      this.waypoints.splice(index, 1);
    },
  },
};
</script>

<template>
  <div>
    <h2>Waypoint Planner</h2>
    <CRow>
      <CCol :md="12">
        <CCard class="mb-4">
          <CCardBody>
            <CRow>
              <CCol>
                <div id="map"></div>
              </CCol>
            </CRow>

            <CRow>
                <div class="waypoint-table">
                  <h4>Waypoints</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Latitude</th>
                        <th>Longitude</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(waypoint, index) in waypoints" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>{{ waypoint.lat.toFixed(6) }}</td>
                        <td>{{ waypoint.lng.toFixed(6) }}</td>
                        <td>
                          <button @click="removeWaypoint(index)">Delete</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
            </CRow>

          </CCardBody>
        </CCard>
      </CCol>
    </CRow>

    <CRow>
      <CCol :md="12">
        <CCard class="mb-4">
          <CCardBody>
            <CRow>
              <CCol :sm="5">
                <h4 id="traffic" class="card-title mb-0">Traffic</h4>
                <div class="small text-body-secondary">January - July 2023</div>
              </CCol>
              <CCol :sm="7" class="d-none d-md-block">
                <CButton color="primary" class="float-end">
                  <CIcon icon="cil-cloud-download" />
                </CButton>
                <CButtonGroup
                  class="float-end me-3"
                  role="group"
                  aria-label="Basic outlined example"
                >
                  <CButton color="secondary" variant="outline">Day</CButton>
                  <CButton color="secondary" variant="outline" active>Month</CButton>
                  <CButton color="secondary" variant="outline">Year</CButton>
                </CButtonGroup>
              </CCol>
            </CRow>
            <CRow>
              <MainChart style="height: 300px; max-height: 300px; margin-top: 40px" />
            </CRow>
          </CCardBody>
          <CCardFooter>
            <CRow
              :xs="{ cols: 1, gutter: 4 }"
              :sm="{ cols: 2 }"
              :lg="{ cols: 4 }"
              :xl="{ cols: 5 }"
              class="mb-2 text-center"
            >
              <CCol>
                <div class="text-body-secondary">Visits</div>
                <div class="fw-semibold text-truncate">29.703 Users (40%)</div>
                <CProgress class="mt-2" color="success" thin :precision="1" :value="40" />
              </CCol>
              <CCol>
                <div class="text-body-secondary">Unique</div>
                <div class="fw-semibold text-truncate">24.093 Users (20%)</div>
                <CProgress class="mt-2" color="info" thin :precision="1" :value="20" />
              </CCol>
              <CCol>
                <div class="text-body-secondary">Pageviews</div>
                <div class="fw-semibold text-truncate">78.706 Views (60%)</div>
                <CProgress class="mt-2" color="warning" thin :precision="1" :value="60" />
              </CCol>
              <CCol>
                <div class="text-body-secondary">New Users</div>
                <div class="fw-semibold text-truncate">22.123 Users (80%)</div>
                <CProgress class="mt-2" color="danger" thin :precision="1" :value="80" />
              </CCol>
              <CCol class="d-none d-xl-block">
                <div class="text-body-secondary">Bounce Rate</div>
                <div class="fw-semibold text-truncate">Average Rate (40.15%)</div>
                <CProgress class="mt-2" :value="40" thin :precision="1" />
              </CCol>
            </CRow>
          </CCardFooter>
        </CCard>
      </CCol>
    </CRow>
    
  </div>
</template>


<style>
#map {
  width: 100%;
  height: 500px;
}

.waypoint-table {
  margin-top: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #f4f4f4;
}
</style>