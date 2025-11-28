<template>
  <div class="modal fade" :id="modalId" tabindex="-1" ref="modal">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">
            <i class="bi bi-file-medical me-2"></i>Medical Record
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" v-if="record">
          <!-- Patient & Visit Info -->
          <div class="row mb-4">
            <div class="col-md-6">
              <div class="bg-light rounded-3 p-3">
                <h6 class="text-muted small mb-2">PATIENT</h6>
                <p class="fw-semibold mb-0">{{ record.patient_name || 'N/A' }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="bg-light rounded-3 p-3">
                <h6 class="text-muted small mb-2">VISIT DATE</h6>
                <p class="fw-semibold mb-0">{{ formatDate(record.visit_date || record.created_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Tabs -->
          <ul class="nav nav-tabs mb-3">
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'details' }"
                @click="activeTab = 'details'"
              >
                <i class="bi bi-file-text me-1"></i>Details
              </button>
            </li>
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'prescription' }"
                @click="activeTab = 'prescription'"
              >
                <i class="bi bi-capsule me-1"></i>Prescription
                <span v-if="hasPrescription" class="badge bg-success ms-1">
                  {{ prescriptionCount }}
                </span>
              </button>
            </li>
          </ul>

          <!-- Details Tab -->
          <div v-show="activeTab === 'details'">
            <!-- Symptoms -->
            <div class="mb-4">
              <h6 class="fw-semibold text-primary mb-2">
                <i class="bi bi-activity me-2"></i>Symptoms
              </h6>
              <p class="mb-0">{{ record.symptoms || 'Not recorded' }}</p>
            </div>

            <!-- Diagnosis -->
            <div class="mb-4">
              <h6 class="fw-semibold text-success mb-2">
                <i class="bi bi-clipboard2-pulse me-2"></i>Diagnosis
              </h6>
              <p class="mb-0">{{ record.diagnosis || 'Not recorded' }}</p>
            </div>

            <!-- Treatment -->
            <div class="mb-4">
              <h6 class="fw-semibold text-info mb-2">
                <i class="bi bi-bandaid me-2"></i>Treatment
              </h6>
              <p class="mb-0">{{ record.treatment || 'Not recorded' }}</p>
            </div>

            <!-- Vitals -->
            <div v-if="hasVitals" class="mb-4">
              <h6 class="fw-semibold text-warning mb-2">
                <i class="bi bi-heart-pulse me-2"></i>Vitals
              </h6>
              <div class="row g-2">
                <div v-if="record.vitals?.blood_pressure" class="col-md-3 col-6">
                  <div class="bg-light rounded p-2 text-center">
                    <small class="text-muted d-block">Blood Pressure</small>
                    <strong>{{ record.vitals.blood_pressure }}</strong>
                  </div>
                </div>
                <div v-if="record.vitals?.heart_rate" class="col-md-3 col-6">
                  <div class="bg-light rounded p-2 text-center">
                    <small class="text-muted d-block">Heart Rate</small>
                    <strong>{{ record.vitals.heart_rate }} bpm</strong>
                  </div>
                </div>
                <div v-if="record.vitals?.temperature" class="col-md-3 col-6">
                  <div class="bg-light rounded p-2 text-center">
                    <small class="text-muted d-block">Temperature</small>
                    <strong>{{ record.vitals.temperature }}°F</strong>
                  </div>
                </div>
                <div v-if="record.vitals?.weight" class="col-md-3 col-6">
                  <div class="bg-light rounded p-2 text-center">
                    <small class="text-muted d-block">Weight</small>
                    <strong>{{ record.vitals.weight }} kg</strong>
                  </div>
                </div>
                <div v-if="record.vitals?.height" class="col-md-3 col-6">
                  <div class="bg-light rounded p-2 text-center">
                    <small class="text-muted d-block">Height</small>
                    <strong>{{ record.vitals.height }} cm</strong>
                  </div>
                </div>
                <div v-if="record.vitals?.oxygen_saturation" class="col-md-3 col-6">
                  <div class="bg-light rounded p-2 text-center">
                    <small class="text-muted d-block">SpO2</small>
                    <strong>{{ record.vitals.oxygen_saturation }}%</strong>
                  </div>
                </div>
              </div>
            </div>

            <!-- Doctor Notes -->
            <div v-if="showDoctorNotes && record.doctor_notes" class="mb-4">
              <h6 class="fw-semibold text-secondary mb-2">
                <i class="bi bi-journal-text me-2"></i>Doctor's Notes
              </h6>
              <div class="bg-light rounded-3 p-3">
                <p class="mb-0 small">{{ record.doctor_notes }}</p>
              </div>
            </div>

            <!-- Follow-up -->
            <div v-if="record.follow_up_date" class="mb-4">
              <h6 class="fw-semibold text-danger mb-2">
                <i class="bi bi-calendar-event me-2"></i>Follow-up
              </h6>
              <p class="mb-0">
                <span class="badge bg-danger-subtle text-danger">
                  {{ formatDate(record.follow_up_date) }}
                </span>
                <span v-if="record.follow_up_notes" class="ms-2 text-muted small">
                  {{ record.follow_up_notes }}
                </span>
              </p>
            </div>

            <!-- Doctor Info -->
            <div v-if="record.doctor_name" class="border-top pt-3 mt-4">
              <small class="text-muted">
                <i class="bi bi-person-badge me-1"></i>
                Attended by: <strong>Dr. {{ record.doctor_name }}</strong>
                <span v-if="record.department_name"> ({{ record.department_name }})</span>
              </small>
            </div>
          </div>

          <!-- Prescription Tab -->
          <div v-show="activeTab === 'prescription'">
            <PrescriptionView 
              :prescription="record.prescription_items"
              :show-instructions="true"
              :show-print="true"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import PrescriptionView from './PrescriptionView.vue';

export default {
  name: 'MedicalRecordModal',
  components: {
    PrescriptionView
  },
  props: {
    record: {
      type: Object,
      default: null
    },
    showDoctorNotes: {
      type: Boolean,
      default: false
    },
    modalId: {
      type: String,
      default: 'medicalRecordModal'
    }
  },
  data() {
    return {
      modal: null,
      activeTab: 'details'
    };
  },
  computed: {
    hasVitals() {
      return this.record?.vitals && Object.keys(this.record.vitals).some(k => this.record.vitals[k]);
    },
    hasPrescription() {
      return this.record?.prescription_items.length > 0;
    },
    prescriptionCount() {
      return this.record?.prescription_items.length || 0;
    }
  },
  methods: {
    show() {
      this.activeTab = 'details';
      this.modal?.show();
    },
    hide() {
      this.modal?.hide();
    },
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>

<style scoped>
.nav-tabs .nav-link {
  color: #6c757d;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  font-weight: 500;
}
</style>