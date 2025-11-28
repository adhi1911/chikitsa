<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <div class="row align-items-center">
        <!-- Date & Time -->
        <div class="col-md-2 text-center mb-3 mb-md-0">
          <div class="bg-primary-subtle rounded p-3">
            <div class="text-primary fw-bold fs-4">{{ dayOfMonth }}</div>
            <div class="text-primary small">{{ monthYear }}</div>
            <div class="text-muted small mt-1">{{ formattedTime }}</div>
          </div>
        </div>

        <!-- Doctor Info -->
        <div class="col-md-5 mb-3 mb-md-0">
          <h6 class="fw-semibold mb-1">{{ appointment.doctor_name }}</h6>
          <p class="text-muted small mb-1">
            <i class="bi bi-hospital me-1"></i>{{ appointment.department_name || 'General' }}
          </p>
          <p v-if="appointment.booking_notes" class="text-muted small mb-0">
            <i class="bi bi-chat-left-text me-1"></i>{{ appointment.booking_notes }}
          </p>
          <!-- Debug: Show appointment ID -->
          <small class="text-muted">ID: {{ appointment.id }}</small>
        </div>

        <!-- Status -->
        <div class="col-md-2 mb-3 mb-md-0">
          <span class="badge" :class="statusClass">
            <i :class="statusIcon" class="me-1"></i>
            {{ statusText }}
          </span>
        </div>

        <!-- Actions -->
        <div class="col-md-3 text-md-end">
          <template v-if="isUpcoming">
            <button class="btn btn-sm btn-outline-primary me-2" @click="$emit('reschedule')">
              <i class="bi bi-calendar-event me-1"></i>Reschedule
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="$emit('cancel')">
              <i class="bi bi-x-lg me-1"></i>Cancel
            </button>
          </template>
          <template v-else-if="appointment.status === 'completed'">
            <button class="btn btn-sm btn-outline-info" @click="onViewRecord">
              <i class="bi bi-file-medical me-1"></i>View Record
            </button>
          </template>
          <template v-else>
            <span class="text-muted small">No actions available</span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppointmentCard',
  props: {
    appointment: { type: Object, required: true }
  },
  emits: ['cancel', 'reschedule', 'view-record'],
  computed: {
    dayOfMonth() {
      return new Date(this.appointment.appointment_date).getDate();
    },
    monthYear() {
      return new Date(this.appointment.appointment_date).toLocaleDateString('en-IN', { 
        month: 'short', year: 'numeric' 
      });
    },
    formattedTime() {
      const time = this.appointment.appointment_time;
      if (!time) return '';
      const [h, m] = time.split(':');
      const hour = parseInt(h);
      return `${hour % 12 || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    },
    isUpcoming() {
      const today = new Date().toISOString().split('T')[0];
      return this.appointment.status === 'scheduled' && this.appointment.appointment_date >= today;
    },
    statusClass() {
      switch (this.appointment.status) {
        case 'scheduled': return 'bg-primary-subtle text-primary';
        case 'completed': return 'bg-success-subtle text-success';
        case 'cancelled': return 'bg-danger-subtle text-danger';
        case 'no_show': return 'bg-warning-subtle text-warning';
        default: return 'bg-secondary-subtle text-secondary';
      }
    },
    statusIcon() {
      switch (this.appointment.status) {
        case 'scheduled': return 'bi bi-clock';
        case 'completed': return 'bi bi-check-circle';
        case 'cancelled': return 'bi bi-x-circle';
        case 'no_show': return 'bi bi-exclamation-circle';
        default: return 'bi bi-question-circle';
      }
    },
    statusText() {
      return this.appointment.status?.charAt(0).toUpperCase() + this.appointment.status?.slice(1).replace('_', ' ');
    }
  },
  methods: {
    onViewRecord() {
      console.log('AppointmentCard emitting view-record for:', this.appointment.id, this.appointment.doctor_name);
      this.$emit('view-record');
    }
  }
};
</script>