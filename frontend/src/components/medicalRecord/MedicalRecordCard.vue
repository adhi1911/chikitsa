<template>
  <div class="card border-0 shadow-sm mb-3" :class="{ 'border-start border-4 border-success': highlighted }">
    <div class="card-body">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div>
          <h6 class="fw-semibold mb-1">{{ record.diagnosis || 'No Diagnosis' }}</h6>
          <small class="text-muted">
            <i class="bi bi-calendar me-1"></i>{{ formatDate(record.visit_date || record.created_at) }}
            <span v-if="record.doctor_name" class="ms-2">
              <i class="bi bi-person me-1"></i>Dr. {{ record.doctor_name }}
            </span>
          </small>
        </div>
        <div class="btn-group btn-group-sm">
          <button 
            class="btn btn-outline-primary"
            @click="$emit('view', record)"
            title="View Details"
          >
            <i class="bi bi-eye"></i>
          </button>
          <button 
            v-if="showPrint"
            class="btn btn-outline-secondary"
            @click="$emit('print', record)"
            title="Print"
          >
            <i class="bi bi-printer"></i>
          </button>
        </div>
      </div>

      <!-- Content Preview -->
      <div class="row g-3">
        <!-- Symptoms -->
        <div v-if="record.symptoms" class="col-md-6">
          <div class="small">
            <span class="text-muted fw-medium">Symptoms:</span>
            <p class="mb-0 text-truncate-2">{{ record.symptoms }}</p>
          </div>
        </div>

        <!-- Treatment -->
        <div v-if="record.treatment_notes" class="col-md-6">
          <div class="small">
            <span class="text-muted fw-medium">Treatment:</span>
            <p class="mb-0 text-truncate-2">{{ record.treatment_notes }}</p>
          </div>
        </div>
      </div>

      <!-- Prescription Preview -->
      <div v-if="record.prescriptions && record.prescriptions.length > 0" class="mt-3">
        <div class="d-flex align-items-center mb-2">
          <i class="bi bi-capsule text-success me-2"></i>
          <span class="small text-muted fw-medium">Prescription ({{ record.prescriptions.length }} items)</span>
        </div>
        <div class="d-flex flex-wrap gap-1">
          <span 
            v-for="(med, index) in record.prescriptions.slice(0, 3)" 
            :key="index"
            class="badge bg-light text-dark"
          >
            {{ med.medicine_name }}
          </span>
          <span v-if="record.prescriptions.length > 3" class="badge bg-secondary">
            +{{ record.prescriptions.length - 3 }} more
          </span>
        </div>
      </div>

      <!-- Follow-up -->
      <div v-if="record.followup_date" class="mt-3 pt-3 border-top">
        <small class="text-warning">
          <i class="bi bi-calendar-event me-1"></i>
          Follow-up: {{ formatDate(record.followup_date) }}
        </small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MedicalRecordCard',
  props: {
    record: {
      type: Object,
      required: true
    },
    highlighted: {
      type: Boolean,
      default: false
    },
    showPrint: {
      type: Boolean,
      default: true
    }
  },
  emits: ['view', 'print'],
  methods: {
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    }
  }
};
</script>

