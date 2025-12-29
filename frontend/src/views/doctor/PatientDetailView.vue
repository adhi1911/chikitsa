<template>
  <div class="patient-detail-view">
    <!-- Back Button & Header -->
    <div class="d-flex align-items-center mb-4">
      <button class="btn btn-outline-secondary me-3" @click="$router.back()">
        <i class="bi bi-arrow-left"></i>
      </button>
      <div>
        <h4 class="mb-0 fw-bold">Patient History</h4>
        <small class="text-muted">Complete medical records and prescriptions</small>
      </div>
    </div>

    <LoadingSpinner v-if="loading" text="Loading patient history..." />

    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div v-else>
      <!-- Patient Info Card -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-auto">
              <div class="avatar-lg bg-primary-subtle rounded-circle d-flex align-items-center justify-content-center">
                <span class="text-primary fw-bold fs-3">{{ getInitials(patient.full_name) }}</span>
              </div>
            </div>
            <div class="col">
              <h5 class="mb-1 fw-semibold">{{ patient.full_name }}</h5>
              <div class="text-muted small">
                <span v-if="patient.age" class="me-3">
                  <i class="bi bi-calendar me-1"></i>{{ patient.age }} years
                </span>
                <span v-if="patient.gender" class="me-3">
                  <i class="bi bi-gender-ambiguous me-1"></i>{{ patient.gender }}
                </span>
                <span v-if="patient.phone" class="me-3">
                  <i class="bi bi-telephone me-1"></i>{{ patient.phone }}
                </span>
                <span v-if="patient.email">
                  <i class="bi bi-envelope me-1"></i>{{ patient.email }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <div class="text-end">
                <div class="badge bg-success-subtle text-success mb-1">
                  {{ records.length }} Records
                </div>
                <div class="small text-muted">
                  Last visit: {{ lastVisitDate }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Row -->
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6">
          <div class="card border-0 bg-primary-subtle h-100">
            <div class="card-body text-center">
              <h3 class="mb-1 fw-bold text-primary">{{ stats.totalVisits }}</h3>
              <small class="text-muted">Total Visits</small>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="card border-0 bg-success-subtle h-100">
            <div class="card-body text-center">
              <h3 class="mb-1 fw-bold text-success">{{ stats.prescriptions }}</h3>
              <small class="text-muted">Prescriptions</small>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="card border-0 bg-warning-subtle h-100">
            <div class="card-body text-center">
              <h3 class="mb-1 fw-bold text-warning">{{ stats.pendingFollowups }}</h3>
              <small class="text-muted">Pending Follow-ups</small>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="card border-0 bg-info-subtle h-100">
            <div class="card-body text-center">
              <h3 class="mb-1 fw-bold text-info">{{ firstVisitDate }}</h3>
              <small class="text-muted">First Visit</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Medical Records -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-0 py-3">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-file-medical me-2 text-primary"></i>Medical Records
            </h5>
            <div class="d-flex gap-2">
              <select class="form-select form-select-sm" v-model="filterType" style="width: auto;">
                <option value="all">All Records</option>
                <option value="with_prescription">With Prescription</option>
                <option value="with_followup">With Follow-up</option>
              </select>
            </div>
          </div>
        </div>
        <div class="card-body p-0">
          <div v-if="filteredRecords.length === 0" class="text-center py-5">
            <i class="bi bi-file-medical text-muted fs-1"></i>
            <p class="text-muted mt-2">No records found</p>
          </div>

          <!-- Records Timeline -->
          <div v-else class="records-timeline">
            <div 
              v-for="record in filteredRecords" 
              :key="record.id"
              class="record-item border-bottom"
            >
              <div class="p-4">
                <!-- Record Header -->
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <span class="badge bg-primary">
                        <i class="bi bi-calendar-event me-1"></i>
                        {{ formatDate(record.created_at) }}
                      </span>
                      <span v-if="record.prescription_items?.length" class="badge bg-success-subtle text-success">
                        <i class="bi bi-capsule me-1"></i>
                        {{ record.prescription_items.length }} medicines
                      </span>
                      <span v-if="record.followup_date" class="badge bg-warning-subtle text-warning">
                        <i class="bi bi-calendar-check me-1"></i>
                        Follow-up: {{ formatDate(record.followup_date) }}
                      </span>
                    </div>
                    <small class="text-muted">
                      <i class="bi bi-person-badge me-1"></i>{{ record.doctor_name }}
                      <span v-if="record.department" class="ms-2">
                        <i class="bi bi-building me-1"></i>{{ record.department }}
                      </span>
                    </small>
                  </div>
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="toggleExpand(record.id)"
                  >
                    <i :class="expanded[record.id] ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
                  </button>
                </div>

                <!-- Diagnosis Summary -->
                <div class="mb-2">
                  <strong class="text-dark">Diagnosis:</strong>
                  <span class="ms-2">{{ record.diagnosis }}</span>
                </div>

                <!-- Symptoms -->
                <div v-if="record.symptoms" class="mb-2 small text-muted">
                  <strong>Symptoms:</strong> {{ record.symptoms }}
                </div>

                <!-- Expanded Content -->
                <div v-show="expanded[record.id]" class="mt-3 pt-3 border-top">
                  <!-- Treatment Notes -->
                  <div v-if="record.treatment_notes" class="mb-3">
                    <h6 class="fw-semibold text-info mb-2">
                      <i class="bi bi-bandaid me-2"></i>Treatment Notes
                    </h6>
                    <p class="mb-0 bg-light rounded p-3 small">{{ record.treatment_notes }}</p>
                  </div>

                  <!-- Doctor Notes (Private) -->
                  <div v-if="record.doctor_notes" class="mb-3">
                    <h6 class="fw-semibold text-secondary mb-2">
                      <i class="bi bi-journal-text me-2"></i>Doctor's Notes
                      <span class="badge bg-secondary-subtle text-secondary ms-2">Private</span>
                    </h6>
                    <p class="mb-0 bg-light rounded p-3 small fst-italic">{{ record.doctor_notes }}</p>
                  </div>

                  <!-- Prescription -->
                  <div v-if="record.prescription_items?.length" class="mb-3">
                    <h6 class="fw-semibold text-success mb-2">
                      <i class="bi bi-capsule me-2"></i>Prescription
                    </h6>
                    <div class="table-responsive">
                      <table class="table table-sm table-bordered mb-0">
                        <thead class="table-light">
                          <tr>
                            <th>Medicine</th>
                            <th>Dosage</th>
                            <th>Frequency</th>
                            <th>Duration</th>
                            <th>Instructions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="med in record.prescription_items" :key="med.id">
                            <td class="fw-medium">{{ med.medicine_name }}</td>
                            <td>{{ med.dosage || '-' }}</td>
                            <td>
                              <span class="badge bg-info-subtle text-info">
                                {{ formatFrequency(med.frequency) }}
                              </span>
                            </td>
                            <td>{{ med.duration || '-' }}</td>
                            <td class="small text-muted">{{ med.instructions || '-' }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <!-- Follow-up Info -->
                  <div v-if="record.followup_date" class="mb-3">
                    <h6 class="fw-semibold text-warning mb-2">
                      <i class="bi bi-calendar-event me-2"></i>Follow-up Scheduled
                    </h6>
                    <div class="bg-warning-subtle rounded p-3">
                      <strong>{{ formatDate(record.followup_date) }}</strong>
                      <span v-if="isFollowupOverdue(record.followup_date)" class="badge bg-danger ms-2">
                        Overdue
                      </span>
                      <span v-else-if="isFollowupUpcoming(record.followup_date)" class="badge bg-success ms-2">
                        Upcoming
                      </span>
                    </div>
                  </div>

                  <!-- Actions -->
                  <div class="d-flex gap-2 mt-3">
                    <button 
                      class="btn btn-sm btn-outline-secondary"
                      @click="printRecord(record)"
                    >
                      <i class="bi bi-printer me-1"></i>Print
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';

export default {
  name: 'PatientDetailView',
  components: {
    LoadingSpinner
  },
  data() {
    return {
      loading: true,
      error: null,
      patient: {},
      records: [],
      expanded: {},
      filterType: 'all'
    };
  },
  computed: {
    patientId() {
      return this.$route.params.id;
    },
    isAdmin(){
      return this.$store.getters['auth/userRole'] === 'admin';
    },
    apiBasePath() {
      return this.isAdmin ? '/admin' : '/doctor';
    },
    filteredRecords() {
      if (this.filterType === 'with_prescription') {
        return this.records.filter(r => r.prescription_items?.length > 0);
      }
      if (this.filterType === 'with_followup') {
        return this.records.filter(r => r.followup_date);
      }
      return this.records;
    },
    stats() {
      const today = new Date().toISOString().split('T')[0];
      return {
        totalVisits: this.records.length,
        prescriptions: this.records.filter(r => r.prescription_items?.length > 0).length,
        pendingFollowups: this.records.filter(r => r.followup_date && r.followup_date >= today).length
      };
    },
    lastVisitDate() {
      if (this.records.length === 0) return 'N/A';
      return this.formatDate(this.records[0].created_at);
    },
    firstVisitDate() {
      if (this.records.length === 0) return 'N/A';
      const firstRecord = this.records[this.records.length - 1];
      return this.formatShortDate(firstRecord.created_at);
    }
  },
  methods: {
    async fetchPatientHistory() {
      try {
        this.loading = true;
        this.error = null;

        const response = await api.get(`${this.apiBasePath}/patients/${this.patientId}/history`);
        
        if (response.data.status === 'success') {
          this.patient = response.data.data.patient || {};
          this.records = response.data.data.records || [];
          
          // Auto-expand first record
          if (this.records.length > 0) {
            this.expanded[this.records[0].id] = true;
          }
        }
      } catch (err) {
        console.error('Failed to fetch patient history:', err);
        this.error = err.response?.data?.message || 'Failed to load patient history';
      } finally {
        this.loading = false;
      }
    },

    toggleExpand(recordId) {
      this.expanded[recordId] = !this.expanded[recordId];
    },

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
    },

    formatShortDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short'
      });
    },

    formatFrequency(frequency) {
      if (!frequency) return '-';
      const map = {
        once_daily: 'Once Daily',
        twice_daily: 'Twice Daily',
        thrice_daily: 'Thrice Daily',
        four_times_daily: '4x Daily',
        every_4_hours: 'Every 4 Hrs',
        every_6_hours: 'Every 6 Hrs',
        every_8_hours: 'Every 8 Hrs',
        as_needed: 'As Needed',
        before_meals: 'Before Meals',
        after_meals: 'After Meals',
        at_bedtime: 'At Bedtime'
      };
      return map[frequency] || frequency;
    },

    isFollowupOverdue(date) {
      if (!date) return false;
      return new Date(date) < new Date();
    },

    isFollowupUpcoming(date) {
      if (!date) return false;
      const followup = new Date(date);
      const today = new Date();
      const weekFromNow = new Date();
      weekFromNow.setDate(today.getDate() + 7);
      return followup >= today && followup <= weekFromNow;
    },

    printRecord(record) {
      // Simple print implementation
      const printContent = `
        <h2>Medical Record</h2>
        <p><strong>Date:</strong> ${this.formatDate(record.created_at)}</p>
        <p><strong>Patient:</strong> ${this.patient.full_name}</p>
        <p><strong>Doctor:</strong> ${record.doctor_name}</p>
        <hr>
        <p><strong>Diagnosis:</strong> ${record.diagnosis}</p>
        <p><strong>Symptoms:</strong> ${record.symptoms || 'N/A'}</p>
        <p><strong>Treatment:</strong> ${record.treatment_notes || 'N/A'}</p>
      `;
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`<html><head><title>Medical Record</title></head><body>${printContent}</body></html>`);
      printWindow.document.close();
      printWindow.print();
    }
  },
  mounted() {
    this.fetchPatientHistory();
  }
};
</script>

<style scoped>
.avatar-lg {
  width: 72px;
  height: 72px;
}

.record-item {
  transition: background-color 0.2s;
}

.record-item:hover {
  background-color: #f8f9fa;
}

.record-item:last-child {
  border-bottom: none !important;
}
</style>