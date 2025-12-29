<template>
  <div class="card border-0 shadow-sm h-100 patient-card">
    <div class="card-body">
      <!-- Header -->
      <div class="d-flex align-items-center mb-3">
        <div class="avatar bg-primary-subtle rounded-circle me-3">
          <span class="text-primary fw-bold">{{ getInitials(patient.full_name) }}</span>
        </div>
        <div class="flex-grow-1 overflow-hidden">
          <h6 class="mb-0 fw-semibold text-truncate">{{ patient.full_name }}</h6>
          <small class="text-muted">{{ patient.email || 'No email' }}</small>
        </div>
      </div>

      <!-- Info -->
      <div class="small mb-3">
        <div class="d-flex justify-content-between mb-1">
          <span class="text-muted">Phone:</span>
          <span>{{ patient.phone || 'N/A' }}</span>
        </div>
        <div class="d-flex justify-content-between mb-1">
          <span class="text-muted">Total Visits:</span>
          <span class="fw-medium">{{ patient.total_visits || 0 }}</span>
        </div>
        <div class="d-flex justify-content-between">
          <span class="text-muted">Last Visit:</span>
          <span>{{ formatDate(patient.last_visit) }}</span>
        </div>
      </div>

      <!-- Follow-up Badge -->
      <div v-if="patient.pending_followup" class="mb-3">
        <span class="badge bg-warning-subtle text-warning">
          <i class="bi bi-calendar-event me-1"></i>
          Follow-up: {{ formatDate(patient.followup_date) }}
        </span>
      </div>

      <!-- Actions -->
      <div class="d-flex gap-2">
        <button 
          class="btn btn-sm btn-outline-primary flex-grow-1"
          @click="$emit('view', patient)"
        >
          <i class="bi bi-eye me-1"></i>View Details
        </button>
        <button 
          class="btn btn-sm btn-outline-success"
          @click="$emit('view-history', patient)"
          title="Medical History"
        >
          <i class="bi bi-clock-history"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PatientCard',
  props: {
    patient: {
      type: Object,
      required: true
    }
  },
  emits: ['view', 'view-history'],
  methods: {
    getInitials(name) {
      if (!name) return '?';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    }
  }
};
</script>

<style scoped>
.patient-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.patient-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1) !important;
}

.avatar {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>