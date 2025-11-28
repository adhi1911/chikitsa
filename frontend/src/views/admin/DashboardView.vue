<template>
  <div class="admin-dashboard">
    <div class="row align-items-center bg-white rounded shadow-sm px-4 py-3 mb-4">
      <div class="col-md-8 d-flex align-items-center">
        <span class="rounded-circle me-3" style="width:20px;height:20px;background:var(--primary-color);"></span>
        <div>
          <h1 class="fw-semibold mb-0" style="font-size:1.5rem;">
            Welcome back, Admin!
          </h1>
          <p class="text-muted mb-0 small">
            Here's whats happening at Chikitsa today
          </p>
        </div>
      </div>
      <div class="col-md-4 text-end">
        <span class="text-secondary fw-medium mb-1 d-block" style="font-size:0.95rem;">{{ formattedDate }}</span>
        <span class="fw-semibold" style="font-size:1.1rem;color:var(--primary-color);">{{ formattedTime }}</span>
      </div>
    </div>

    <!-- loading state -->
     <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading Dashboard...</p>
     </div>

     
     <!-- stats content -->
      <div v-else >
      <p>{{ stats }}</p>
        <div class="row g-4 mb-4">

          <!-- patients -->
           <div class="col-md-6 col-lg-3">
              <div class="card border-0 shadow-sm h-100 stat-card">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-itmes start">
                    <div>
                      <p class="text-muted mb-1 small text-uppercase fw-semibold">Total Patients</p>
                      <h2 class="fw-bold mb-0"> {{ stats.users?.total_patients || 0 }}</h2>
                    </div>
                    <div class="stat-icon bg-primary-subtle rounded-3 p-3">
                      <i class="bi bi-people fs-4 text-primary"></i>
                    </div>
                  </div>
                  <div class="mt-3">
                    <router-link to="/admin/patients" class="text-decoration-none small">
                      View all patients <i class="bi bi-arrow-right"></i>
                    </router-link>
                  </div>
                </div>
              </div>
           </div>

           <!-- doctors -->
           <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100 stat-">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <p class="text-muted mb-1 small text-uppercase fw-sembibold">Total Doctors</p>
                    <h2 class="fw-bold mb-0"> {{ stats.users?.total_doctors || 0 }}</h2>
                  </div>
                  <div class="stat-icon bg-success-subtle rounded-3 p-3">
                    <i class="bi bi-person-badge fs-4 text-success"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/doctors" class="text-decoration-none small">
                    View all doctors <i class="bi bi-arrow-right"></i>
                  </router-link>
                </div>
              </div>
            </div>
           </div>

           <!-- departments -->
          <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100 stat-card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <p class="text-muted mb-1 small text-uppercase fw-semibold">Departments</p>
                    <h2 class="fw-bold mb-0">{{ stats.departments?.active || 0 }}</h2>
                    <small class="text-muted">of {{ stats.departments?.total || 0 }} total</small>
                  </div>
                  <div class="stat-icon bg-info-subtle rounded-3 p-3">
                    <i class="bi bi-building fs-4 text-info"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/departments" class="text-decoration-none small">
                    Manage departments <i class="bi bi-arrow-right"></i>
                  </router-link>
                </div>
              </div>
            </div>
          </div>

          <!-- today's appointments -->
          <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100 stat-card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <p class="text-muted mb-1 small text-uppercase fw-semibold">Today's Appointments</p>
                    <h2 class="fw-bold mb-0">{{ stats.appointments?.today || 0 }}</h2>
                  </div>
                  <div class="stat-icon bg-warning-subtle rounded-3 p-3">
                    <i class="bi bi-calendar-check fs-4 text-warning"></i>
                  </div>
                </div>
                <div class="mt-3">
                  <router-link to="/admin/appointments" class="text-decoration-none small">
                    View appointments <i class="bi bi-arrow-right"></i>
                  </router-link>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- second row appointment stats -->
        <div class="row g-4 mb-4">
          <div class="col-lg-">
            <div class="card border-0 shadow-sm h-">
              <div class="card-header bg-white border-0 py-">
                <h5 class="mb-0 fw-semibold">
                  <i class="bi bi-bar-chart-line-fill me-2 text-secondary"></i>
                  Appointment Overview
                </h5>
              </div>
              <div class="card-body">
                <div class="row g-4">
                  <div class="col-md-3 text-center">
                    <div class="p-3 bg-light rounded-3">
                      <h3 class="fw-bold text-primary mb-1">{{ stats.appointments?.total || 0 }}</h3>
                      <small class="text-muted">Total</small>
                    </div>
                  </div>
                  <div class="col-md-3 text-center">
                    <div class="p-3 bg-light rounded-3">
                      <h3 class="fw-bold text-info mb-1">{{ stats.appointments?.scheduled || 0 }}</h3>
                      <small class="text-muted">Scheduled</small>
                    </div>
                  </div>
                  <div class="col-md-3 text-center">
                    <div class="p-3 bg-light rounded-3">
                      <h3 class="fw-bold text-success mb-1">{{ stats.appointments?.completed || 0 }}</h3>
                      <small class="text-muted">Completed</small>
                    </div>
                  </div>
                  <div class="col-md-3 text-center">
                    <div class="p-3 bg-light rounded-3">
                      <h3 class="fw-bold text-danger mb-1">{{ stats.appointments?.cancelled || 0 }}</h3>
                      <small class="text-muted">Cancelled</small>
                    </div>
                  </div>
                </div>

              <div class="mt-4">
                <div class="d-flex justify-content-between mb-2">
                  <small class="text-muted">Completion Rate</small>
                  <small class="fw-semibold">{{ completionRate }}%</small>
                </div>
                <div class="progress" style="height: 10px;">
                  <div 
                    class="progress-bar bg-success" 
                    :style="{ width: completionRate + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            </div>
          </div>

          <!-- quick actions -->
           <div class="col-lg-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-0 py-5">
                <h5 class="mb-0 fw-semibold">
                  <i class="bi bi-lightning me-2 text-warning"></i>Quick Actions
                </h5>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <router-link to="/admin/doctors" class="btn btn-outline-primary text-start">
                    <i class="bi bi-person-plus me-2"></i>Add New Doctor
                  </router-link>
                  <router-link to="/admin/departments" class="btn btn-outline-success text-start">
                    <i class="bi bi-building-add me-2"></i>Add Department
                  </router-link>
                  <router-link to="/admin/appointments" class="btn btn-outline-info text-start">
                    <i class="bi bi-calendar-plus me-2"></i>View Appointments
                  </router-link>
                  <router-link to="/admin/patients" class="btn btn-outline-secondary text-start">
                    <i class="bi bi-people me-2"></i>Manage Patients
                  </router-link>
                </div>
              </div>
            </div>
           </div>
          
           <!-- thrid row, medical records -->
          <div class="row g-4">
            <div class="col-md-6">
              <div class="card border-0 shadow-sm">
                <div class="card-header bg-white border-0 py-3">
                  <h5 class="mb-0 fw-semibold">
                    <i class="bi bi-file-medical me-2 text-danger"></i>Medical Records
                  </h5>
                </div>
                <div class="card-body">
                  <div class="row text-center">
                    <div class="col-6">
                      <h3 class="fw-bold text-primary">{{ stats.medical_records?.total || 0 }}</h3>
                      <small class="text-muted">Total Records</small>
                    </div>
                    <div class="col-6">
                      <h3 class="fw-bold text-success">{{ stats.medical_records?.this_month || 0 }}</h3>
                      <small class="text-muted">This Month</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card border-0 shadow-sm">
                <div class="card-header bg-white border-0 py-3">
                  <h5 class="mb-0 fw-semibold">
                    <i class="bi bi-calendar-week me-2 text-info"></i>This Week
                  </h5>
                </div>
                <div class="card-body">
                  <div class="row text-center">
                    <div class="col-6">
                      <h3 class="fw-bold text-primary">{{ stats.appointments?.this_week || 0 }}</h3>
                      <small class="text-muted">Appointments</small>
                    </div>
                    <div class="col-6">
                      <h3 class="fw-bold text-success">{{ stats.users?.active_users || 0 }}</h3>
                      <small class="text-muted">Active Users</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            </div>
        </div>
      </div> <!--else div-->
  </div>
</template>

<script>
import api from '@/services/api';
export default {
  name: 'AdminDashboard',
  data() {
    return {
      now: new Date(),
      loading: true, 
      stats: {
        users: {},
        departments: {},
        appointments: {},
        medical_records: {}
      },
      timer: null
    };
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
    },
    completionRate(){
      const total = this.stats.appointments?.total || 0;
      const completed = this.stats.appointments?.completed || 0;
      if (total === 0) return '0%';
      return ((completed / total) * 100).toFixed(2) + '%';
    }
  },
  mounted() {
    this.fetchstats();
    this.timer = setInterval(() => {
      this.now = new Date()
    }, 1000)
  },
  beforeUnmount() {
    if (this.timer){
      clearInterval(this.timer)
    }
  },
  methods: {
    async fetchstats(){
      try {
        this.loading = true;
        const response = await api.get('admin/dashboard/stats');
        if(response.data.status === 'success'){
          this.stats = response.data.data.stats;
        }
      } catch(error){
        console.error('Error fetching stats:', error);
      }finally{
        this.loading = false;
      }
    }
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