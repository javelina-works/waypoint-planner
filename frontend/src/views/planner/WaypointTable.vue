<template>
    <div>
      <h2>Waypoints</h2>
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
              <button @click="$emit('remove-waypoint', index)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    props: ["waypoints"],
  };
  </script>
  
  <style>
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: center;
  }
  </style>
  