<template>
  <div class="dashboard-view">
    <PageHeader title="Dashboard" :subtitle="greeting" />

    <LoadingSpinner v-if="loading" />

    <div v-else>
      <!-- Stats -->
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6">
          <StatsCard icon="bi bi-calendar-event" :value="stats.upcoming" label="Upcoming" variant="primary" />
        </div>
        <div class="col-md-3 col-6">
          <StatsCard icon="bi bi-check-circle" :value="stats.completed" label="Completed" variant="success" />
        </div>
        <div class="col-md-3 col-6">
          <StatsCard icon="bi bi-x-circle" :value="stats.cancelled" label="Cancelled" variant="danger" />
        </div>
        <div class="col-md-3 col-6">
          <StatsCard icon="bi bi-file-medical" :value="stats.records" label="Records" variant="info" />
        </div>
      </div>

      <div class="row g-4">
        <!-- Upcoming Appointments -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-calendar-check me-2 text-primary"></i>Upcoming Appointments
              </h5>
              <router-link to="/patient/doctors" class="btn btn-primary btn-sm">
                <i class="bi bi-plus-lg me-1"></i>Book
              </router-link>
            </div>
            <div class="card-body p-0">
              <div v-if="upcomingAppointments.length === 0" class="text-center py-5">
                <i class="bi bi-calendar-x text-muted fs-1"></i>
                <p class="text-muted mt-2">No upcoming appointments</p>
                <router-link to="/patient/doctors" class="btn btn-outline-primary btn-sm">Find a Doctor</router-link>
              </div>
              <div v-else class="list-group list-group-flush">
                <div v-for="apt in upcomingAppointments" :key="apt.id" class="list-group-item px-4 py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <div class="fw-semibold">{{ apt.doctor_name }}</div>
                      <small class="text-muted">{{ apt.department_name || 'General' }}</small>
                    </div>
                    <div class="text-end">
                      <div class="text-primary fw-medium">{{ formatDate(apt.appointment_date) }}</div>
                      <small class="text-muted">{{ formatTime(apt.appointment_time) }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="upcomingAppointments.length > 0" class="card-footer bg-white border-0">
              <router-link to="/patient/appointments" class="text-decoration-none small">
                View all appointments <i class="bi bi-arrow-right"></i>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-lightning me-2 text-warning"></i>Quick Actions
              </h5>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <router-link to="/patient/doctors" class="btn btn-outline-primary">
                  <i class="bi bi-search me-2"></i>Find Doctor
                </router-link>
                <router-link to="/patient/appointments" class="btn btn-outline-success">
                  <i class="bi bi-calendar-check me-2"></i>My Appointments
                </router-link>
                <router-link to="/patient/records" class="btn btn-outline-info">
                  <i class="bi bi-file-medical me-2"></i>Medical Records
                </router-link>
              </div>
            </div>
          </div>

          <!-- Recent Record -->
          <div v-if="recentRecord" class="card border-0 shadow-sm">
            <div class="card-header bg-white py-3">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-clock-history me-2 text-info"></i>Recent Visit
              </h5>
            </div>
            <div class="card-body">
              <p class="mb-1 fw-medium">{{ recentRecord.doctor_name }}</p>
              <p class="text-muted small mb-2">{{ formatDate(recentRecord.created_at) }}</p>
              <p class="mb-0"><strong>Diagnosis:</strong> {{ recentRecord.diagnosis || 'N/A' }}</p>
              <router-link to="/patient/records" class="btn btn-sm btn-outline-info mt-3">View Details</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import { mapGetters } from 'vuex';
import PageHeader from '@/components/common/PageHeader.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import StatsCard from '@/components/common/StatsCard.vue';

export default {
  name: 'PatientDashboard',
  components: { PageHeader, LoadingSpinner, StatsCard },
  data() {
    return {
      loading: true,
      stats: { upcoming: 0, completed: 0, cancelled: 0, records: 0 },
      upcomingAppointments: [],
      recentRecord: null
    };
  },
  computed: {
    ...mapGetters('auth', ['user']),
    greeting() {
      const hour = new Date().getHours();
      const time = hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : 'Evening';
      return `Good ${time}, ${this.user?.first_name || 'Patient'}`;
    }
  },
  methods: {
    async fetchDashboard() {
      try {
        this.loading = true;
        
        // Fetch appointments and records separately to handle errors
        let appointments = [];
        let records = [];

        try {
          const aptsRes = await api.get('/patient/appointments');
          appointments = aptsRes.data?.data?.appointments || [];
        } catch (e) {
          console.error('Failed to fetch appointments:', e);
        }

        try {
          const recordsRes = await api.get('/patient/records');
          records = recordsRes.data?.data?.records || [];
        } catch (e) {
          console.error('Failed to fetch records:', e);
        }

        // Calculate stats
        const today = new Date().toISOString().split('T')[0];
        
        this.stats = {
          upcoming: appointments.filter(a => a.status === 'scheduled' && a.appointment_date >= today).length,
          completed: appointments.filter(a => a.status === 'completed').length,
          cancelled: appointments.filter(a => a.status === 'cancelled').length,
          records: records.length
        };

        // Upcoming appointments (max 5)
        this.upcomingAppointments = appointments
          .filter(a => a.status === 'scheduled' && a.appointment_date >= today)
          .sort((a, b) => a.appointment_date.localeCompare(b.appointment_date))
          .slice(0, 5);

        // Recent record
        this.recentRecord = records.length > 0 ? records[0] : null;

      } catch (e) {
        console.error('Dashboard error:', e);
      } finally {
        this.loading = false;
      }
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    },
    formatTime(time) {
      if (!time) return '';
      const [h, m] = time.split(':');
      const hour = parseInt(h);
      return `${hour % 12 || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    }
  },
  mounted() {
    this.fetchDashboard();
  }
};
</script>