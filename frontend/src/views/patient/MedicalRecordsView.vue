<template>
  <div class="medical-records-view">
    <PageHeader 
      title="My Medical Records" 
      subtitle="View your consultation history and prescriptions"
    />

    <!-- Search & Filter -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body py-3">
        <div class="row g-3 align-items-center">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search by doctor, diagnosis..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filterDepartment">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept" :value="dept">
                {{ dept }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filterDoctor">
              <option value="">All Doctors</option>
              <option v-for="doc in doctors" :key="doc" :value="doc">
                {{ doc }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <button 
              class="btn btn-outline-secondary w-100" 
              @click="clearFilters"
              :disabled="!hasFilters"
            >
              <i class="bi bi-x-lg me-1"></i>Clear
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-2 text-muted">Loading your medical records...</p>
    </div>

    <!-- Empty State -->
    <EmptyState 
      v-else-if="filteredRecords.length === 0"
      icon="bi bi-file-medical"
      :message="emptyMessage"
    >
      <router-link to="/patient/doctors" class="btn btn-primary mt-3">
        <i class="bi bi-calendar-plus me-2"></i>Book an Appointment
      </router-link>
    </EmptyState>

    <!-- Records List -->
    <div v-else class="row g-4">
      <div v-for="record in filteredRecords" :key="record.id" class="col-12">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="row align-items-center">
              <!-- Date -->
              <div class="col-md-2 text-center mb-3 mb-md-0">
                <div class="bg-primary-subtle rounded-3 p-3">
                  <div class="text-primary fw-bold fs-4">
                    {{ getDayOfMonth(record.created_at) }}
                  </div>
                  <div class="text-primary small">
                    {{ getMonthYear(record.created_at) }}
                  </div>
                </div>
              </div>

              <!-- Details -->
              <div class="col-md-7 mb-3 mb-md-0">
                <h6 class="fw-semibold mb-1">{{ record.doctor_name }}</h6>
                <p class="text-muted small mb-2">
                  <i class="bi bi-hospital me-1"></i>{{ record.department }}
                </p>
                
                <!-- Diagnosis -->
                <div v-if="record.diagnosis" class="mb-2">
                  <span class="badge bg-info-subtle text-info me-2">Diagnosis</span>
                  <span class="text-dark">{{ truncate(record.diagnosis, 100) }}</span>
                </div>

                <!-- Symptoms -->
                <div v-if="record.symptoms" class="small text-muted">
                  <i class="bi bi-activity me-1"></i>
                  {{ truncate(record.symptoms, 80) }}
                </div>

                <!-- Prescription Count -->
                <div v-if="record.prescription_items?.length" class="mt-2">
                  <span class="badge bg-success-subtle text-success">
                    <i class="bi bi-capsule me-1"></i>
                    {{ record.prescription_items.length }} medication(s)
                  </span>
                </div>

                <!-- Follow-up -->
                <div v-if="record.followup_date" class="mt-2">
                  <span class="badge bg-warning-subtle text-warning">
                    <i class="bi bi-calendar-event me-1"></i>
                    Follow-up: {{ formatDate(record.followup_date) }}
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="col-md-3 text-md-end">
                <button 
                  class="btn btn-outline-primary"
                  @click="viewRecord(record)"
                >
                  <i class="bi bi-eye me-2"></i>View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Medical Record Modal -->
    <MedicalRecordModal
      ref="recordModal"
      :record="selectedRecord"
      modal-id="patientMedicalRecordModal"
    />
  </div>
</template>

<script>
import api from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import EmptyState from '@/components/common/EmptyState.vue';
import MedicalRecordModal from '@/components/medicalRecord/MedicalRecordModal.vue';

export default {
  name: 'MedicalRecordsView',
  components: {
    PageHeader,
    EmptyState,
    MedicalRecordModal
  },
  data() {
    return {
      loading: true,
      records: [],
      searchQuery: '',
      filterDepartment: '',
      filterDoctor: '',
      selectedRecord: null
    };
  },
  computed: {
    departments() {
      const depts = [...new Set(this.records.map(r => r.department).filter(Boolean))];
      return depts.sort();
    },
    doctors() {
      const docs = [...new Set(this.records.map(r => r.doctor_name).filter(Boolean))];
      return docs.sort();
    },
    hasFilters() {
      return this.searchQuery || this.filterDepartment || this.filterDoctor;
    },
    filteredRecords() {
      let result = [...this.records];

      // Search filter
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        result = result.filter(r => 
          r.doctor_name?.toLowerCase().includes(q) ||
          r.department?.toLowerCase().includes(q) ||
          r.diagnosis?.toLowerCase().includes(q) ||
          r.symptoms?.toLowerCase().includes(q)
        );
      }

      // Department filter
      if (this.filterDepartment) {
        result = result.filter(r => r.department === this.filterDepartment);
      }

      // Doctor filter
      if (this.filterDoctor) {
        result = result.filter(r => r.doctor_name === this.filterDoctor);
      }

      // Sort by date (newest first)
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

      return result;
    },
    emptyMessage() {
      if (this.hasFilters) {
        return 'No records match your search criteria';
      }
      return 'No medical records found. Book an appointment to get started.';
    }
  },
  methods: {
    async fetchRecords() {
      try {
        this.loading = true;
        const res = await api.get('/patient/records');
        this.records = res.data?.data?.records || [];
      } catch (e) {
        console.error('Failed to fetch records:', e);
      } finally {
        this.loading = false;
      }
    },

    clearFilters() {
      this.searchQuery = '';
      this.filterDepartment = '';
      this.filterDoctor = '';
    },

    getDayOfMonth(date) {
      return new Date(date).getDate();
    },

    getMonthYear(date) {
      return new Date(date).toLocaleDateString('en-IN', { 
        month: 'short', 
        year: 'numeric' 
      });
    },

    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    },

    truncate(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    },

    viewRecord(record) {
      this.selectedRecord = {
        ...record,
        notes: record.treatment_notes,
        treatment: record.treatment_notes
      };
      this.$refs.recordModal.show();
    }
  },
  mounted() {
    this.fetchRecords();
  }
};
</script>

<style scoped>
.card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1) !important;
}
</style>