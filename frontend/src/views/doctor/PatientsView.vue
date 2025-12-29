<template>
  <div class="patients-view">
    <PageHeader 
      title="My Patients" 
      subtitle="View patients you have consulted"
    />

    <!-- Search & Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label small fw-medium">Search Patient</label>
            <div class="input-group">
              <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                v-model="searchQuery"
                placeholder="Name, email or phone..."
                @input="debouncedSearch"
              >
            </div>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-medium">Sort By</label>
            <select class="form-select" v-model="sortBy" @change="fetchPatients">
              <option value="recent">Most Recent Visit</option>
              <option value="name">Name (A-Z)</option>
              <option value="visits">Most Visits</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-medium">Filter</label>
            <select class="form-select" v-model="filter" @change="fetchPatients">
              <option value="all">All Patients</option>
              <option value="recent">Last 30 Days</option>
              <option value="followup">Pending Follow-up</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-lg me-1"></i>Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <StatsCard 
          icon="bi bi-people"
          :value="stats.total_patients"
          label="Total Patients"
          variant="primary"
        />
      </div>
      <div class="col-md-4">
        <StatsCard 
          icon="bi bi-calendar-check"
          :value="stats.this_month"
          label="This Month"
          variant="success"
        />
      </div>
      <div class="col-md-4">
        <StatsCard 
          icon="bi bi-arrow-repeat"
          :value="stats.followups_pending"
          label="Pending Follow-ups"
          variant="warning"
        />
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="loading" variant="success" text="Loading patients..." />

    <!-- Empty State -->
    <EmptyState 
      v-else-if="patients.length === 0"
      icon="bi bi-people"
      message="No patients found"
    >
      <p class="text-muted small">Patients will appear here after consultations</p>
    </EmptyState>

    <!-- Patients Grid -->
    <div v-else class="row g-4">
      <div 
        v-for="patient in patients" 
        :key="patient.id"
        class="col-lg-4 col-md-6"
      >
        <PatientCard 
          :patient="patient"
          @view="viewPatient"
          @view-history="openHistory"
        />
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
      <nav>
        <ul class="pagination pagination-sm">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="goToPage(currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </button>
          </li>
          <li 
            v-for="page in visiblePages" 
            :key="page"
            class="page-item"
            :class="{ active: page === currentPage }"
          >
            <button class="page-link" @click="goToPage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="goToPage(currentPage + 1)">
              <i class="bi bi-chevron-right"></i>
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Patient Detail Modal -->
    <div class="modal fade" id="patientDetailModal" tabindex="-1" ref="patientDetailModal">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="bi bi-person me-2"></i>Patient Details
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedPatient">
            <!-- Patient Info -->
            <div class="row mb-4">
              <div class="col-md-8">
                <div class="d-flex align-items-center">
                  <div class="avatar-lg bg-primary-subtle rounded-circle me-3">
                    <span class="text-primary fw-bold fs-4">{{ getInitials(selectedPatient.full_name) }}</span>
                  </div>
                  <div>
                    <h4 class="mb-1">{{ selectedPatient.full_name }}</h4>
                    <p class="text-muted mb-0">
                      <i class="bi bi-envelope me-2"></i>{{ selectedPatient.email || 'N/A' }}
                      <span class="mx-2">|</span>
                      <i class="bi bi-telephone me-2"></i>{{ selectedPatient.phone || 'N/A' }}
                    </p>
                  </div>
                </div>
              </div>
              <div class="col-md-4 text-md-end">
                <div class="text-muted small">
                  <div><strong>Total Visits:</strong> {{ selectedPatient.total_visits || 0 }}</div>
                  <div><strong>Last Visit:</strong> {{ formatDate(selectedPatient.last_visit) }}</div>
                </div>
              </div>
            </div>

            <!-- Patient Stats -->
            <div class="row g-3 mb-4">
              <div class="col-md-4">
                <div class="bg-light rounded-3 p-3 text-center">
                  <h4 class="text-success mb-1">{{ patientStats.completed || 0 }}</h4>
                  <small class="text-muted">Completed Visits</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-light rounded-3 p-3 text-center">
                  <h4 class="text-primary mb-1">{{ patientStats.upcoming || 0 }}</h4>
                  <small class="text-muted">Upcoming Appointments</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-light rounded-3 p-3 text-center">
                  <h4 class="text-warning mb-1">{{ patientStats.cancelled || 0 }}</h4>
                  <small class="text-muted">Cancelled/No Show</small>
                </div>
              </div>
            </div>

            <!-- Medical History -->
            <MedicalHistory
              title="Medical History"
              :records="patientRecords"
              :loading="loadingRecords"
              :show-filters="true"
              :show-doctor-notes="true"
              :initial-limit="5"
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/services/api';

import PageHeader from '@/components/common/PageHeader.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import EmptyState from '@/components/common/EmptyState.vue';
import StatsCard from '@/components/common/StatsCard.vue';
import MedicalHistory from '@/components/medicalRecord/MedicalHistory.vue';
import PatientCard from '@/components/doctor/PatientCard.vue';

export default {
  name: 'PatientsView',
  components: {
    PageHeader,
    LoadingSpinner,
    EmptyState,
    StatsCard,
    MedicalHistory,
    PatientCard
  },
  data() {
    return {
      loading: true,
      loadingRecords: false,
      patients: [],
      selectedPatient: null,
      patientRecords: [],
      patientStats: {},
      searchQuery: '',
      sortBy: 'recent',
      filter: 'all',
      currentPage: 1,
      perPage: 12,
      totalPatients: 0,
      stats: {
        total_patients: 0,
        this_month: 0,
        followups_pending: 0
      },
      searchTimeout: null,
      modals: {}
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalPatients / this.perPage);
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
    async fetchPatients() {
      try {
        this.loading = true;
        const params = {
          page: this.currentPage,
          per_page: this.perPage,
          sort_by: this.sortBy,
          filter: this.filter
        };

        if (this.searchQuery) {
          params.search = this.searchQuery;
        }

        const response = await api.get('/doctor/patients', { params });

        if (response.data.status === 'success') {
          this.patients = response.data.data.patients;
          this.totalPatients = response.data.data.total || this.patients.length;
        }
      } catch (error) {
        console.error('Failed to fetch patients:', error);
      } finally {
        this.loading = false;
      }
    },

    async fetchStats() {
      try {
        const response = await api.get('/doctor/patients/stats');
        if (response.data.status === 'success') {
          this.stats = response.data.data.stats;
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1;
        this.fetchPatients();
      }, 300);
    },

    resetFilters() {
      this.searchQuery = '';
      this.sortBy = 'recent';
      this.filter = 'all';
      this.currentPage = 1;
      this.fetchPatients();
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        this.fetchPatients();
      }
    },

    async viewPatient(patient) {
      this.selectedPatient = patient;
      this.patientRecords = [];
      this.patientStats = {};
      this.modals.patientDetail.show();
      await this.fetchPatientDetails(patient.id);
    },

    async fetchPatientDetails(patientId) {
      try {
        this.loadingRecords = true;

        // Fetch medical records
        const recordsRes = await api.get(`/doctor/patients/${patientId}/records`);
        if (recordsRes.data.status === 'success') {
          this.patientRecords = recordsRes.data.data.records;
        }

        // Fetch patient stats
        const statsRes = await api.get(`/doctor/patients/${patientId}/stats`);
        if (statsRes.data.status === 'success') {
          this.patientStats = statsRes.data.data.stats;
        }
      } catch (error) {
        console.error('Failed to fetch patient details:', error);
      } finally {
        this.loadingRecords = false;
      }
    },

    openHistory(patient) {

    //   console.log(patient.id)
        this.$router.push(`/doctor/patients/${patient.id}`);
    },

    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    },

    getInitials(name) {
      if (!name) return '?';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
  },

  mounted() {
    this.modals = {
      patientDetail: new Modal(this.$refs.patientDetailModal)
    };
    this.fetchPatients();
    this.fetchStats();
  }
};
</script>

<style scoped>
.avatar-lg {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination .page-link {
  color: #198754;
}

.pagination .page-item.active .page-link {
  background-color: #198754;
  border-color: #198754;
}
</style>