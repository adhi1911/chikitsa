<template>
  <div>
    <!-- Today's Info Card -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h5 class="mb-1 fw-semibold">{{ formattedToday }}</h5>
            <p class="text-muted mb-0">{{ dayName }}</p>
          </div>
          <div class="col-md-6 text-md-end mt-3 mt-md-0">
            <div v-if="todaySchedule" class="d-flex justify-content-md-end gap-3">
              <div class="text-center">
                <div class="small text-muted">Working Hours</div>
                <div class="fw-semibold text-success">
                  {{ formatTime(todaySchedule.start_time) }} - {{ formatTime(todaySchedule.end_time) }}
                </div>
              </div>
              <div class="text-center">
                <div class="small text-muted">Slot Duration</div>
                <div class="fw-semibold">{{ todaySchedule.slot_duration || 30 }} min</div>
              </div>
            </div>
            <div v-else>
              <span class="badge bg-secondary-subtle text-secondary fs-6">
                <i class="bi bi-moon-stars me-1"></i>Day Off
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-3 col-6">
        <div class="card border-0 bg-primary-subtle h-100">
          <div class="card-body text-center py-3">
            <h3 class="mb-0 fw-bold text-primary">{{ stats.total }}</h3>
            <small class="text-muted">Total</small>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card border-0 bg-warning-subtle h-100">
          <div class="card-body text-center py-3">
            <h3 class="mb-0 fw-bold text-warning">{{ stats.pending }}</h3>
            <small class="text-muted">Pending</small>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card border-0 bg-success-subtle h-100">
          <div class="card-body text-center py-3">
            <h3 class="mb-0 fw-bold text-success">{{ stats.completed }}</h3>
            <small class="text-muted">Completed</small>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card border-0 bg-danger-subtle h-100">
          <div class="card-body text-center py-3">
            <h3 class="mb-0 fw-bold text-danger">{{ stats.cancelled }}</h3>
            <small class="text-muted">Cancelled/No-show</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointments Timeline -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-0 py-3">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-calendar-check me-2 text-success"></i>Today's Appointments
        </h5>
      </div>
      <div class="card-body">
        <LoadingSpinner v-if="loading" size="sm" text="Loading appointments..." />

        <div v-else-if="!appointments || appointments.length === 0" class="text-center py-5">
          <i class="bi bi-calendar-x text-muted fs-1"></i>
          <p class="text-muted mt-2 mb-0">No appointments scheduled for today</p>
        </div>

        <div v-else class="timeline">
          <div 
            v-for="appointment in appointments" 
            :key="appointment.id"
            class="timeline-item"
          >
            <div class="timeline-marker" :class="getStatusClass(appointment.status)"></div>
            <div class="timeline-content">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="fw-semibold text-success">
                    {{ formatTime(appointment.appointment_time) }}
                  </div>
                  <div class="fw-medium">{{ appointment.patient_name }}</div>
                  <small class="text-muted">{{ appointment.booking_notes || 'General Consultation' }}</small>
                </div>
                <span 
                  class="badge"
                  :class="getStatusBadgeClass(appointment.status)"
                >
                  {{ formatStatus(appointment.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';

export default {
  name: 'TodaySchedule',
  components: { LoadingSpinner },
  props: {
    workingHours: { type: Array, default: () => [] },
    appointments: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  computed: {
    formattedToday() {
      return new Date().toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    },
    dayName() {
      return new Date().toLocaleDateString('en-IN', { weekday: 'long' });
    },
    todayDayOfWeek() {
      let dow = new Date().getDay() - 1;
      if (dow < 0) dow = 6;
      return dow;
    },
    todaySchedule() {
      if (!this.workingHours) return null;
      return this.workingHours.find(
        wh => wh.day_of_week === this.todayDayOfWeek && wh.is_active
      ) || null;
    },
    stats() {
      const appointments = this.appointments || [];
      return {
        total: appointments.length,
        pending: appointments.filter(a => a.status === 'scheduled').length,
        completed: appointments.filter(a => a.status === 'completed').length,
        cancelled: appointments.filter(a => ['cancelled', 'no_show'].includes(a.status)).length
      };
    }
  },
  methods: {
    formatTime(time) {
      if (!time) return '';
      const [hours, minutes] = time.split(':');
      const h = parseInt(hours);
      return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
    },
    getStatusClass(status) {
      const map = {
        scheduled: 'bg-warning',
        completed: 'bg-success',
        cancelled: 'bg-danger',
        no_show: 'bg-secondary'
      };
      return map[status] || 'bg-secondary';
    },
    getStatusBadgeClass(status) {
      const map = {
        scheduled: 'bg-warning-subtle text-warning',
        completed: 'bg-success-subtle text-success',
        cancelled: 'bg-danger-subtle text-danger',
        no_show: 'bg-secondary-subtle text-secondary'
      };
      return map[status] || 'bg-secondary-subtle text-secondary';
    },
    formatStatus(status) {
      const map = {
        scheduled: 'Scheduled',
        completed: 'Completed',
        cancelled: 'Cancelled',
        no_show: 'No Show'
      };
      return map[status] || status;
    }
  }
};
</script>

<style scoped>
.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #dee2e6;
}

.timeline-item {
  position: relative;
  padding-bottom: 1.5rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -26px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #dee2e6;
}

.timeline-content {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
}
</style>