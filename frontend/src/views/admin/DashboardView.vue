<template>
  <div class="admin-dashboard bg-light min-vh-100">
    <!-- Welcome Header Section -->
    <div class="container py-4">
      <div class="row align-items-center bg-white rounded shadow-sm px-4 py-3 mb-4">
        <div class="col-md-8 d-flex align-items-center">
          <span class="rounded-circle me-3" style="width:20px;height:20px;background:var(--primary-color);"></span>
          <h1 class="fw-semibold mb-0" style="font-size:1.7rem;color:var(--dark-color);">
            <div class="text-muted display-6">Welcome back Admin</div>
          </h1>
        </div>
        <div class="col-md-4 text-end">
          <div class="d-flex flex-column align-items-end">
            <span class="text-secondary fw-medium mb-1" style="font-size:0.95rem;">{{ formattedDate }}</span>
            <span class="fw-semibold" style="font-size:1.1rem;color:var(--primary-color);">{{ formattedTime }}</span>
          </div>
        </div>
      </div>

      <div class="row justify-content-center">
        <div class="col-12 col-md-10">
          <div class="border rounded bg-white py-5 px-3 text-center text-secondary" style="border-style:dashed;">
            Dashboard content will be added here...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      now: new Date()
    }
  },
  computed: {
    formattedDate() {
      return this.now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formattedTime() {
      return this.now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      this.now = new Date()
    }, 1000)
  },
  beforeDestroy() {
    clearInterval(this.timer)
  }
}
</script>

<style scoped>
.gradient-text {
  background: linear-gradient(90deg, var(--accent-color), #45d7d0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>