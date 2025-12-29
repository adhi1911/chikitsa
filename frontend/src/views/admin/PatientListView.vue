<template>
  <div class="patient-list-view">
    <PageHeader 
      title="Patients" 
      subtitle="Manage patient records and information"
    >
      <template #actions>
        <button class="btn btn-primary" @click="openAddModal">
          <i class="bi bi-person-plus me-2"></i>Add Patient
        </button>
      </template>
    </PageHeader>

    <!-- stat cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <StatsCard
          title="Total Patients"
          :value="patients.length"
          icon="bi bi-people"
          variant="primary"
        />
      </div>
      <div class="col-md-3">
        <StatsCard
          title="Active"
          :value="activePatients"
          icon="bi bi-person-check"
          variant="success"
        />
      </div>
      <div class="col-md-3">
        <StatsCard
          title="Male"
          :value="malePatients"
          icon="bi bi-gender-male"
          variant="info"
        />
      </div>
      <div class="col-md-3">
        <StatsCard
          title="Female"
          :value="femalePatients"
          icon="bi bi-gender-female"
          variant="warning"
        />
      </div>
    </div>

    <!-- filters -->
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
                placeholder="Search by name, email, phone..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filterGender">
              <option value="">All Genders</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filterBloodGroup">
              <option value="">All Blood Groups</option>
              <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filterStatus">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
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

    <!-- loading statee -->
    <LoadingSpinner v-if="loading" message="Loading patients..." />

    <!-- empty state -->
    <EmptyState 
      v-else-if="filteredPatients.length === 0"
      icon="bi bi-people"
      :message="emptyMessage"
    >
      <button v-if="!hasFilters" class="btn btn-primary mt-3" @click="openAddModal">
        <i class="bi bi-person-plus me-2"></i>Add First Patient
      </button>
    </EmptyState>

    <!-- table for patients -->
    <div v-else class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Patient</th>
              <th>Contact</th>
              <th>Age / Gender</th>
              <th>Blood Group</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="patient in paginatedPatients" :key="patient.id">
              
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar-sm rounded-circle me-3" :class="getAvatarClass(patient.gender)">
                    {{ getInitials(patient.full_name) }}
                  </div>
                  <div>
                    <div class="fw-semibold">{{ patient.full_name }}</div>
                    <small class="text-muted">ID: {{ patient.id }}</small>
                  </div>
                </div>
              </td>

              <!-- contact-->
              <td>
                <div class="small">
                  <div><i class="bi bi-envelope me-1 text-muted"></i>{{ patient.email }}</div>
                  <div><i class="bi bi-phone me-1 text-muted"></i>{{ patient.phone || '-' }}</div>
                </div>
              </td>

              <!-- age and gender-->
              <td>
                <span v-if="patient.date_of_birth || patient.gender">
                  {{ calculateAge(patient.dob) || '-' }} / {{ formatGender(patient.gender) || '-' }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>

              <!-- blood group -->
              <td>
                <span v-if="patient.blood_group" class="badge bg-danger-subtle text-danger">
                  {{ patient.blood_group }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>

              <!-- status -->
              <td>
                <span 
                  class="badge"
                  :class="patient.is_active !== false ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'"
                >
                  {{ patient.is_active !== false ? 'Active' : 'Inactive' }}
                </span>
              </td>

              <!-- Actions Column -->
              <td>
                <div class="d-flex gap-1">
                  <button 
                    class="btn btn-sm btn-outline-info"
                    @click="openViewModal(patient)"
                    title="View Details"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="openEditModal(patient)"
                    title="Edit"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button
                    class="btn btn-sm"
                    :class="patient.is_active !== false ? 'btn-outline-danger' : 'btn-outline-success'"
                    @click="toggleStatus(patient)">
                     <i :class="patient.is_active ? 'bi bi-person-slash' : 'bi bi-person-check'"></i>                
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDelete(patient)"
                    title="Delete"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                  <button class="btn btn-outline-secondary btn-sm" @click="viewPatient(patient.id)">
                    View
                  </button>
                  <ExportPatientsRecordButton 
                    :patient-id="patient.id"
                    :patient-name="`${patient.first_name} ${patient.last_name}`"
                    :patient-email="patient.email"
                    @exported="onExported"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- paginaton -->
      <div v-if="totalPages > 1" class="card-footer bg-white">
        <div class="d-flex justify-content-between align-items-center">
          <small class="text-muted">
            Showing {{ paginationStart }} to {{ paginationEnd }} of {{ filteredPatients.length }} patients
          </small>
          <nav>
            <ul class="pagination pagination-sm mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="currentPage--">&laquo;</button>
              </li>
              <li 
                v-for="page in visiblePages" 
                :key="page" 
                class="page-item"
                :class="{ active: currentPage === page }"
              >
                <button class="page-link" @click="currentPage = page">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="currentPage++">&raquo;</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- form to create patient -->
    <PatientFormModal 
      ref="formModal"
      @saved="fetchPatients"
    />

    <!-- viewing modal -->
    <PatientViewModal 
      ref="viewModal"
      @edit="onEditFromView"
    />

    <!-- confirm to delete -->
    <ConfirmModal
      ref="deleteModal"
      title="Delete Patient"
      message="Are you sure you want to delete this patient? All their appointments and records will also be deleted. This action cannot be undone."
      confirm-text="Delete"
      confirm-variant="danger"
      :loading="deleting"
      @confirm="deletePatient"
    />
  </div>
</template>

<script>
import api from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import StatsCard from '@/components/common/StatsCard.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import EmptyState from '@/components/common/EmptyState.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import PatientFormModal from '@/components/admin/PatientFormModal.vue';
import PatientViewModal from '@/components/admin/PatientViewModal.vue';
import ExportPatientsRecordButton from '@/components/admin/ExportPatientsRecordButton.vue';

export default {
  name: 'PatientListView',
  components: {
    PageHeader,
    StatsCard,
    LoadingSpinner,
    EmptyState,
    ConfirmModal,
    PatientFormModal,
    PatientViewModal,
    ExportPatientsRecordButton
  },
  data() {
    return {
      loading: true,
      deleting: false,
      patients: [],
      searchQuery: '',
      filterGender: '',
      filterBloodGroup: '',
      filterStatus: '',
      currentPage: 1,
      perPage: 10,
      selectedPatient: null,
      bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    };
  },
  computed: {
    activePatients() {
      return this.patients.filter(p => p.is_active !== false).length;
    },
    malePatients() {
      return this.patients.filter(p => p.gender === 'male').length;
    },
    femalePatients() {
      return this.patients.filter(p => p.gender === 'female').length;
    },
    hasFilters() {
      return this.searchQuery || this.filterGender || this.filterBloodGroup || this.filterStatus;
    },
    filteredPatients() {
      let result = [...this.patients];

      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        result = result.filter(p => 
          p.full_name?.toLowerCase().includes(q) ||
          p.email?.toLowerCase().includes(q) ||
          p.phone?.includes(q)
        );
      }

      // Gender filter
      if (this.filterGender) {
        result = result.filter(p => p.gender === this.filterGender);
      }

      // blood group filter
      if (this.filterBloodGroup) {
        result = result.filter(p => p.blood_group === this.filterBloodGroup);
      }

      // status 
      if (this.filterStatus === 'active') {
        result = result.filter(p => p.is_active !== false);
      } else if (this.filterStatus === 'inactive') {
        result = result.filter(p => p.is_active === false);
      }

      return result;
    },
    totalPages() {
      return Math.ceil(this.filteredPatients.length / this.perPage);
    },
    paginatedPatients() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredPatients.slice(start, start + this.perPage);
    },
    paginationStart() {
      return (this.currentPage - 1) * this.perPage + 1;
    },
    paginationEnd() {
      return Math.min(this.currentPage * this.perPage, this.filteredPatients.length);
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    },
    emptyMessage() {
      if (this.hasFilters) {
        return 'No patients match your search criteria';
      }
      return 'No patients found. Add your first patient to get started.';
    },
  },
  watch: {
    filteredPatients() {
      
      this.currentPage = 1;
    }
  },
  methods: {
    async fetchPatients() {
      try {
        this.loading = true;
        const res = await api.get('/admin/patients');
        this.patients = res.data?.data?.patients || [];
      } catch (e) {
        console.error('Failed to fetch patients:', e);
      } finally {
        this.loading = false;
      }
    },

    getInitials(name) {
      if (!name) return '?';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    },

    getAvatarClass(gender) {
      if (gender === 'male') return 'bg-info-subtle text-info';
      if (gender === 'female') return 'bg-pink-subtle text-pink';
      return 'bg-secondary-subtle text-secondary';
    },

    calculateAge(dob) {
      if (!dob) return null;
      const today = new Date();
      const birth = new Date(dob);
      let age = today.getFullYear() - birth.getFullYear();
      const m = today.getMonth() - birth.getMonth();
      if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
        age--;
      }
      return age;
    },

    formatGender(gender) {
      if (!gender) return null;
      return gender.charAt(0).toUpperCase();
    },

    clearFilters() {
      this.searchQuery = '';
      this.filterGender = '';
      this.filterBloodGroup = '';
      this.filterStatus = '';
    },

    openAddModal() {
      this.$refs.formModal.show();
    },

    openEditModal(patient) {
      this.$refs.formModal.show(patient);
    },

    openViewModal(patient) {
      this.$refs.viewModal.show(patient);
    },

    onEditFromView(patient) {
      this.$refs.viewModal.hide();
      setTimeout(() => {
        this.openEditModal(patient);
      }, 300);
    },

    confirmDelete(patient) {
      this.selectedPatient = patient;
      this.$refs.deleteModal.show();
    },

    async deletePatient() {
      if (!this.selectedPatient) return;

      try {
        this.deleting = true;
        await api.delete(`/admin/patients/${this.selectedPatient.id}`);
        this.$refs.deleteModal.hide();
        this.fetchPatients();
      } catch (e) {
        console.error('Failed to delete patient:', e);
        alert(e.response?.data?.message || 'Failed to delete patient');
      } finally {
        this.deleting = false;
      }
    },
    async toggleStatus(patient) {
      const action = patient.is_active !== false ? 'blacklist' : 'activate';
      if (!confirm(`Are you sure you want to ${action} this patient?`)) {
        return;
      }

      try{
        await api.patch(`/admin/users/${patient.user_id}/status`);
        this.fetchPatients();
      } catch(e){
        console.error(`Failed to ${action} patient:`, e);
        alert(e.response?.data?.message || `Failed to ${action} patient`);
    }
    },
    viewPatient(id){
      this.$router.push(`/admin/patients/${id}`);
    },
    onExported(data) {
      console.log('Patient records exported:', data);
    }
  },
  mounted() {
    this.fetchPatients();
  }
};
</script>

<style scoped>
.avatar-sm {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
}

.bg-pink-subtle {
  background-color: #fce4ec;
}

.text-pink {
  color: #e91e63;
}
</style>