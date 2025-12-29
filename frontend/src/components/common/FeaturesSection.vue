<template>
  <section id="features" class="features-section py-5 bg-light">
    <div class="container">
      <div class="row">
        <div class="col-lg-8 mx-auto text-center mb-5">
          <h2 class="fw-bold text-dark mb-3">Healthcare Excellence</h2>
          <p class="text-muted">Modern technology meets traditional care values</p>
        </div>
      </div>
      
      <div class="row g-4">
        <div class="col-md-4" v-for="feature in features" :key="feature.title">
          <div class="feature-card h-100">
            <div class="feature-icon mb-3" :class="feature.iconColor">
              <i :class="feature.icon"></i>
            </div>
            <h5 class="fw-semibold mb-3">{{ feature.title }}</h5>
            <p class="text-muted">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'FeaturesSection',
  data() {
    return {
      features: [
        {
          icon: 'fas fa-calendar-check',
          iconColor: 'text-primary',
          title: 'Smart Appointments',
          description: 'Intelligent scheduling system that prevents conflicts and optimizes doctor availability.'
        },
        {
          icon: 'fas fa-clipboard-list',
          iconColor: 'text-success',
          title: 'Digital Records',
          description: 'Secure, comprehensive medical history tracking for better patient care continuity.'
        },
        {
          icon: 'fas fa-bell',
          iconColor: 'text-warning',
          title: 'Smart Reminders',
          description: 'Automated notifications for appointments, medications, and follow-up care.'
        }
      ]
    }
  }
}
</script>

<style scoped>
/* Feature Cards */
.features-section {
  position: relative;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  border: none;
  box-shadow: 0 5px 25px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.feature-icon {
  font-size: 2.5rem;
  display: inline-block;
}
</style>