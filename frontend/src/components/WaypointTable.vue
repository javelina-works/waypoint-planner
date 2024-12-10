<template>
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
        <td>{{ waypoint.lat }}</td>
        <td>{{ waypoint.lng }}</td>
        <td>
          <button @click="removeWaypoint(index)">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: "WaypointTable",
  props: ["waypoints"],
  methods: {
    removeWaypoint(index) {
      this.$emit("remove", index);
    },
  },
};
</script>

<style>
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f4f4f4;
}
</style>
