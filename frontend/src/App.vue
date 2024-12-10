<template>
  <CContainer>
    <CRow>
      <CCol>
        <h1>Waypoint Planner Dashboard</h1>
      </CCol>
    </CRow>
    <CRow>
      <CCol sm="6">
        <CWidgetStatsA title="Waypoints" value="5" />
      </CCol>
      <CCol sm="6">
        <CWidgetStatsA title="Routes" value="2" />
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
/* Optional: Add custom styles here */
</style>
