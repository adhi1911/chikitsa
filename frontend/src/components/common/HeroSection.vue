<template>
  <section class="hero">
    <div class="container">
      <div class="row align-items-center min-vh-100 py-5">
        <div class="col-lg-6">
          <div class="hero-content">
            
            <div class="lotus-pattern mb-4">
              <div class="lotus-icon">
                <i class="fas fa-spa text-primary"></i>
              </div>
            </div>
            
            <h1 class="display-3 fw-bold text-dark mb-4">
              चिकित्सा
              <span class="text-primary d-block fs-2 fw-light">Modern Healthcare Management</span>
            </h1>
            
            <p class="lead text-muted mb-5 lh-lg">
              Seamlessly connecting patients, doctors, and administrators through 
              intelligent healthcare technology with the warmth of traditional care.
            </p>
            
            <div class="hero-stats d-flex flex-wrap gap-4 mb-5">
              <div class="stat-item" v-for="stat in stats" :key="stat.label">
                <div class="stat-number fw-bold" :class="stat.color">{{ stat.number }}</div>
                <div class="stat-label text-muted small">{{ stat.label }}</div>
              </div>
            </div>
            
            <div class="hero-actions">
              <router-link to="/register" class="btn btn-primary btn-lg px-5 rounded-pill me-3">
                Get Started
                <i class="fas fa-arrow-right ms-2"></i>
              </router-link>
              <a href="#features" class="btn btn-outline-dark btn-lg px-4 rounded-pill">
                Learn More
              </a>
            </div>
          </div>
        </div>
        
        <div class="col-lg-6">
          <div class="hero-image position-relative">
            <!-- Modern Geometric Pattern with Indian Colors -->
            <div class="geometric-pattern">
              <div class="pattern-circle circle-1"></div>
              <div class="pattern-circle circle-2"></div>
              <div class="pattern-circle circle-3"></div>
            </div>
            
            <!-- Central Medical Icon -->
            <div class="medical-icon-container">
              <div class="medical-icon">
                <i class="fas fa-heartbeat"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
    name: 'HeroSection',
    data() {
    return {
      stats: [
        { number: '500+', label: 'Patients Served', color: 'text-primary' },
        { number: '50+', label: 'Expert Doctors', color: 'text-success' },
        { number: '24/7', label: 'Available', color: 'text-warning' }
      ]
    }
  }
}
</script>
<style>

.hero {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23007bff' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 2;
}

/* Indian Lotus Pattern */
.lotus-pattern {
  display: inline-block;
}

.lotus-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #FF6B35, #F7931E);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

/* Hero Stats */
.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.5rem;
}

/* Geometric Pattern */
.hero-image {
  position: relative;
  height: 500px;
  z-index: 1;
}

.geometric-pattern {
  position: relative;
  width: 100%;
  height: 100%;
}

.pattern-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #FF6B35, #F7931E);
  top: 10%;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.circle-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #4ECDC4, #45B7AF);
  bottom: 20%;
  left: 20%;
  animation: float 8s ease-in-out infinite reverse;
}

.circle-3 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 4s ease-in-out infinite;
}

.medical-icon-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.medical-icon {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: #FF6B35;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  animation: heartbeat 2s ease-in-out infinite;
}

/* Animations */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.1); }
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  25%, 75% { transform: scale(1.05); }
  50% { transform: scale(1.1); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero {
    text-align: center;
  }
  
  .hero-image {
    height: 300px;
    margin-top: 3rem;
  }
  
  .display-3 {
    font-size: 2.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .hero-actions .btn {
    width: 100%;
  }
}

</style>