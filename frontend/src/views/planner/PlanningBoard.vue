<template>
    <div>
      <MapComponent 
        :waypoints="waypoints" 
        @add-waypoint="addWaypoint" 
        @update-waypoint="updateWaypoint"
			/>
      <WaypointTable 
				:waypoints="waypoints" 
				@remove-waypoint="removeWaypoint" 
			/>
    </div>
  </template>
  
  <script>
  import MapComponent from "./MapComponent.vue";
  import WaypointTable from "./WaypointTable.vue";
  
  export default {
    components: { MapComponent, WaypointTable },
    data() {
      return {
        waypoints: [],
      };
    },
    methods: {
      addWaypoint(latLng) {
        this.waypoints.push({ lat: latLng.lat, lng: latLng.lng });
      },
      removeWaypoint(index) {
        this.waypoints.splice(index, 1);
      },
			updateWaypoint({ index, latLng }) {
      // Update the waypoint at the given index
      this.waypoints[index] = { lat: latLng.lat, lng: latLng.lng };
    },
    },
  };
  </script>
  