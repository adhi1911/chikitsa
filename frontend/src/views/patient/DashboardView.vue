<template>
  <div class="dashboard-view text-center">
    <div class="card shadow-sm p-5 mx-auto" style="max-width:500px;">
      <div class="mb-4">
        <i class="bi bi-person-circle fs-1 text-primary"></i>
      </div>
      <h2 class="fw-bold mb-3">Welcome to Your Patient Dashboard</h2>
      <p class="text-muted">Registration and redirection successful.<br>
        You are now logged in as a patient.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardView'
}
</script>

<style scoped>
.dashboard-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
.card {
  border-radius: 1.5rem;
}
</style>