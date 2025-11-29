<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
      <h5 class="mb-0 fw-semibold">
        <i class="bi bi-calendar-check me-2 text-success"></i>{{ title }}
      </h5>
      <slot name="header-actions">
        <router-link v-if="showViewAll" to="/doctor/appointments" class="btn btn-sm btn-outline-success">
          View All
        </router-link>
      </slot>
    </div>
    <div class="card-body p-0">
      <!-- Empty State -->
      <div v-if="appointments.length === 0" class="text-center py-5">
        <i class="bi bi-calendar-x display-4 text-muted opacity-50"></i>
        <p class="mt-2 text-muted">{{ emptyMessage }}</p>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th v-if="showDate">Date</th>
              <th>Time</th>
              <th>Patient</th>
              <th>Status</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="apt in appointments" :key="apt.id">
              <td v-if="showDate">
                <span class="small">{{ formatDate(apt.appointment_date) }}</span>
              </td>
              <td>
                <span class="fw-semibold text-success">{{ formatTime(apt.appointment_time) }}</span>
              </td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar-sm bg-primary-subtle rounded-circle me-2">
                    <span class="text-primary small fw-bold">{{ getInitials(apt.patient_name) }}</span>
                  </div>
                  <div>
                    <div class="fw-medium">{{ apt.patient_name }}</div>
                    <small class="text-muted">{{ apt.booking_notes || 'General Consultation' }}</small>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge" :class="getStatusBadge(apt.status)">
                  {{ formatStatus(apt.status) }}
                </span>
              </td>
              <td class="text-end">
                <div class="btn-group btn-group-sm">
                  <button 
                    v-if="apt.status === 'scheduled'"
                    class="btn btn-success"
                    @click="$emit('start-consultation', apt)"
                    title="Start Consultation"
                  >
                    <i class="bi bi-play-fill"></i>
                  </button>
                  <button 
                    v-if="apt.status === 'scheduled'"
                    class="btn btn-outline-danger"
                    @click="$emit('no-show', apt)"
                    title="No Show"
                  >
                    <i class="bi bi-person-x"></i>
                  </button>
                  <button 
                    v-if="apt.status === 'completed'"
                    class="btn btn-outline-primary"
                    @click="$emit('view-record', apt)"
                    title="View Record"
                  >
                    <i class="bi bi-file-text"></i>
                  </button>
                  <button 
                    v-if="apt.status === 'scheduled'"
                    class="btn btn-outline-secondary"
                    @click="$emit('cancel', apt)"
                    title="Cancel"
                  >
                    <i class="bi bi-x-lg"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppointmentTable',
  props: {
    appointments: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: 'Appointments'
    },
    emptyMessage: {
      type: String,
      default: 'No appointments found'
    },
    showViewAll: {
      type: Boolean,
      default: false
    },
    showDate: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start-consultation', 'no-show', 'view-record', 'cancel'],
  methods: {
    formatTime(time) {
      if (!time) return '';
      const [hours, minutes] = time.split(':');
      const h = parseInt(hours);
      return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', { 
        day: 'numeric', 
        month: 'short'
      });
    },
    getInitials(name) {
      if (!name) return '?';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },
    getStatusBadge(status) {
      const badges = {
        scheduled: 'bg-info-subtle text-info',
        completed: 'bg-success-subtle text-success',
        canceled: 'bg-danger-subtle text-danger',
        no_show: 'bg-warning-subtle text-warning'
      };
      return badges[status] || 'bg-secondary';
    },
    formatStatus(status) {
      return status?.charAt(0).toUpperCase() + status?.slice(1).replace('_', ' ');
    }
  }
};
</script>

<style scoped>
.avatar-sm {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>