<template>
  <div class="patient-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1 fw-bold">
          <i class="bi bi-people me-2 text-primary"></i>Patients
        </h2>
        <p class="text-muted mb-0">Manage registered patients</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Add Patient
      </button>
    </div>

    <!-- Search & Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search by name, email, or phone..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filterGender">
              <option value="">All Genders</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="sortBy">
              <option value="name">Sort by Name</option>
              <option value="date">Sort by Registration Date</option>
              <option value="appointments">Sort by Appointments</option>
            </select>
          </div>
          <div class="col-md-1">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters" title="Reset Filters">
              <i class="bi bi-arrow-counterclockwise"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading patients...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger border-0 shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchPatients">Retry</button>
    </div>

    <!-- Patients Table -->
    <div v-else-if="filteredPatients.length > 0" class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Patient</th>
              <th>Contact</th>
              <th>Gender</th>
              <th>Blood Group</th>
              <th>Appointments</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="patient in paginatedPatients" :key="patient.id">
              <!-- Patient Info -->
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar bg-primary-subtle rounded-circle me-3">
                    <span class="text-primary fw-bold">
                      {{ getInitials(patient.first_name, patient.last_name) }}
                    </span>
                  </div>
                  <div>
                    <h6 class="mb-0">{{ patient.first_name }} {{ patient.last_name }}</h6>
                    <small class="text-muted">ID: {{ patient.id }}</small>
                  </div>
                </div>
              </td>

              <!-- Contact -->
              <td>
                <div>
                  <small class="d-block"><i class="bi bi-envelope me-1"></i>{{ patient.email || '-' }}</small>
                  <small class="d-block"><i class="bi bi-phone me-1"></i>{{ patient.phone || '-' }}</small>
                </div>
              </td>

              <!-- Gender -->
              <td>
                <span class="badge" :class="getGenderBadgeClass(patient.gender)">
                  {{ patient.gender || 'N/A' }}
                </span>
              </td>

              <!-- Blood Group -->
              <td>
                <span class="badge bg-danger-subtle text-danger" v-if="patient.blood_group">
                  {{ patient.blood_group }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>

              <!-- Appointments -->
              <td>
                <span class="badge bg-info-subtle text-info">
                  {{ patient.total_appointments || 0 }} appointments
                </span>
              </td>

              <!-- Actions -->
              <td class="text-center">
                <button 
                  class="btn btn-sm btn-outline-info me-1"
                  @click="viewPatient(patient)"
                  title="View Details"
                >
                  <i class="bi bi-eye"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-primary me-1"
                  @click="editPatient(patient)"
                  title="Edit"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-success me-1"
                  @click="viewHistory(patient)"
                  title="Medical History"
                >
                  <i class="bi bi-file-medical"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-danger"
                  @click="confirmDelete(patient)"
                  title="Delete"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="card-footer bg-white border-0">
        <div class="d-flex justify-content-between align-items-center">
          <small class="text-muted">
            Showing {{ paginationStart }} - {{ paginationEnd }} of {{ filteredPatients.length }} patients
          </small>
          <nav>
            <ul class="pagination pagination-sm mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage--">
                  <i class="bi bi-chevron-left"></i>
                </a>
              </li>
              <li 
                class="page-item" 
                v-for="page in totalPages" 
                :key="page"
                :class="{ active: currentPage === page }"
              >
                <a class="page-link" href="#" @click.prevent="currentPage = page">{{ page }}</a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="currentPage++">
                  <i class="bi bi-chevron-right"></i>
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-people display-1 text-muted opacity-50"></i>
      <h4 class="mt-3 text-muted">No Patients Found</h4>
      <p class="text-muted">{{ searchQuery ? 'Try adjusting your search' : 'No patients registered yet' }}</p>
    </div>

    <!-- View Patient Modal -->
    <div class="modal fade" id="viewModal" tabindex="-1" ref="viewModal">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0 pb-0">
            <div class="d-flex align-items-center">
              <div class="avatar-lg bg-primary-subtle rounded-circle me-3">
                <span class="text-primary fw-bold fs-4">
                  {{ getInitials(selectedPatient?.first_name, selectedPatient?.last_name) }}
                </span>
              </div>
              <div>
                <h5 class="modal-title fw-semibold mb-0">
                  {{ selectedPatient?.first_name }} {{ selectedPatient?.last_name }}
                </h5>
                <small class="text-muted">Patient ID: {{ selectedPatient?.id }}</small>
              </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body pt-4">
            <div class="row g-4">
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">EMAIL</label>
                <p class="mb-0">{{ selectedPatient?.email || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">PHONE</label>
                <p class="mb-0">{{ selectedPatient?.phone || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">GENDER</label>
                <p class="mb-0">{{ selectedPatient?.gender || 'Not specified' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">DATE OF BIRTH</label>
                <p class="mb-0">{{ formatDate(selectedPatient?.dob) || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">BLOOD GROUP</label>
                <p class="mb-0">
                  <span v-if="selectedPatient?.blood_group" class="badge bg-danger-subtle text-danger">
                    {{ selectedPatient?.blood_group }}
                  </span>
                  <span v-else>Not provided</span>
                </p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">TOTAL APPOINTMENTS</label>
                <p class="mb-0">{{ selectedPatient?.total_appointments || 0 }}</p>
              </div>
              <div class="col-12">
                <label class="form-label text-muted small fw-semibold">ADDRESS</label>
                <p class="mb-0">{{ selectedPatient?.address || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">EMERGENCY CONTACT</label>
                <p class="mb-0">{{ selectedPatient?.emergency_contact_name || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted small fw-semibold">EMERGENCY PHONE</label>
                <p class="mb-0">{{ selectedPatient?.emergency_contact_phone || 'Not provided' }}</p>
              </div>
              <div class="col-12" v-if="selectedPatient?.medical_history">
                <label class="form-label text-muted small fw-semibold">MEDICAL HISTORY</label>
                <p class="mb-0">{{ selectedPatient?.medical_history }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="editFromView">
              <i class="bi bi-pencil me-2"></i>Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit/Add Patient Modal -->
    <div class="modal fade" id="editModal" tabindex="-1" ref="editModal">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-semibold">
              <i class="bi bi-person me-2 text-primary"></i>
              {{ isEditing ? 'Edit Patient' : 'Add New Patient' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="savePatient">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">First Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.first_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Last Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.last_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Username <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.username" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email <span class="text-danger">*</span></label>
                  <input type="email" class="form-control" v-model="form.email" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone</label>
                  <input type="text" class="form-control" v-model="form.phone">
                </div>
                <div class="col-md-6" v-if="!isEditing">
                  <label class="form-label">Password <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="form.password" :required="!isEditing">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Gender</label>
                  <select class="form-select" v-model="form.gender">
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Date of Birth</label>
                  <input type="date" class="form-control" v-model="form.dob">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Blood Group</label>
                  <select class="form-select" v-model="form.blood_group">
                    <option value="">Select Blood Group</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                  </select>
                </div>
                <div class="col-12">
                  <label class="form-label">Address</label>
                  <textarea class="form-control" v-model="form.address" rows="2"></textarea>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Emergency Contact Name</label>
                  <input type="text" class="form-control" v-model="form.emergency_contact_name">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Emergency Contact Phone</label>
                  <input type="text" class="form-control" v-model="form.emergency_contact_phone">
                </div>
                <div class="col-12">
                  <label class="form-label">Medical History</label>
                  <textarea class="form-control" v-model="form.medical_history" rows="3"></textarea>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="savePatient" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ isEditing ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-semibold text-danger">
              <i class="bi bi-exclamation-triangle me-2"></i>Delete Patient
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete <strong>{{ selectedPatient?.first_name }} {{ selectedPatient?.last_name }}</strong>?</p>
            <p class="text-muted small mb-0">This action cannot be undone. All patient data including appointments and medical records will be permanently deleted.</p>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deletePatient" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Medical History Modal -->
    <div class="modal fade" id="historyModal" tabindex="-1" ref="historyModal">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-semibold">
              <i class="bi bi-file-medical me-2 text-success"></i>
              Medical History - {{ selectedPatient?.first_name }} {{ selectedPatient?.last_name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingHistory" class="text-center py-4">
              <div class="spinner-border text-primary" role="status"></div>
              <p class="mt-2 text-muted">Loading medical history...</p>
            </div>
            <div v-else-if="medicalHistory.length === 0" class="text-center py-4">
              <i class="bi bi-folder-x display-4 text-muted"></i>
              <p class="mt-2 text-muted">No medical records found</p>
            </div>
            <div v-else>
              <div class="accordion" id="historyAccordion">
                <div class="accordion-item border-0 mb-3 shadow-sm" v-for="(record, index) in medicalHistory" :key="record.id">
                  <h2 class="accordion-header">
                    <button 
                      class="accordion-button" 
                      :class="{ collapsed: index !== 0 }"
                      type="button" 
                      data-bs-toggle="collapse" 
                      :data-bs-target="'#record-' + record.id"
                    >
                      <div class="d-flex justify-content-between align-items-center w-100 me-3">
                        <div>
                          <strong>{{ record.diagnosis }}</strong>
                          <small class="text-muted d-block">Dr. {{ record.doctor_name }} - {{ record.department }}</small>
                        </div>
                        <small class="text-muted">{{ formatDate(record.created_at) }}</small>
                      </div>
                    </button>
                  </h2>
                  <div :id="'record-' + record.id" class="accordion-collapse collapse" :class="{ show: index === 0 }">
                    <div class="accordion-body">
                      <div class="row g-3">
                        <div class="col-md-6">
                          <label class="form-label text-muted small fw-semibold">SYMPTOMS</label>
                          <p>{{ record.symptoms || 'Not recorded' }}</p>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label text-muted small fw-semibold">FOLLOW-UP DATE</label>
                          <p>{{ record.followup_date ? formatDate(record.followup_date) : 'No follow-up scheduled' }}</p>
                        </div>
                        <div class="col-12">
                          <label class="form-label text-muted small fw-semibold">TREATMENT NOTES</label>
                          <p>{{ record.treatment_notes || 'No treatment notes' }}</p>
                        </div>
                        <div class="col-12" v-if="record.prescription_items && record.prescription_items.length > 0">
                          <label class="form-label text-muted small fw-semibold">PRESCRIPTION</label>
                          <div class="table-responsive">
                            <table class="table table-sm table-bordered">
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
                                <tr v-for="item in record.prescription_items" :key="item.id">
                                  <td>{{ item.medicine_name }}</td>
                                  <td>{{ item.dosage || '-' }}</td>
                                  <td>{{ item.frequency || '-' }}</td>
                                  <td>{{ item.duration || '-' }}</td>
                                  <td>{{ item.instructions || '-' }}</td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import { Modal } from 'bootstrap';

export default {
  name: 'PatientListView',
  data() {
    return {
      patients: [],
      loading: true,
      error: null,
      searchQuery: '',
      filterGender: '',
      sortBy: 'name',
      currentPage: 1,
      perPage: 10,
      selectedPatient: null,
      isEditing: false,
      saving: false,
      deleting: false,
      loadingHistory: false,
      medicalHistory: [],
      form: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        password: '',
        gender: '',
        dob: '',
        blood_group: '',
        address: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        medical_history: ''
      },
      modals: {}
    };
  },
  computed: {
    filteredPatients() {
      let result = [...this.patients];

      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(p => 
          p.first_name?.toLowerCase().includes(query) ||
          p.last_name?.toLowerCase().includes(query) ||
          p.email?.toLowerCase().includes(query) ||
          p.phone?.includes(query)
        );
      }

      // Gender filter
      if (this.filterGender) {
        result = result.filter(p => p.gender === this.filterGender);
      }

      // Sort
      result.sort((a, b) => {
        switch (this.sortBy) {
          case 'name':
            return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`);
          case 'date':
            return new Date(b.created_at) - new Date(a.created_at);
          case 'appointments':
            return (b.total_appointments || 0) - (a.total_appointments || 0);
          default:
            return 0;
        }
      });

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
    }
  },
  methods: {
    async fetchPatients() {
      try {
        this.loading = true;
        this.error = null;
        const response = await api.get('/admin/patients');
        if (response.data.status === 'success') {
          this.patients = response.data.data.patients;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch patients';
      } finally {
        this.loading = false;
      }
    },
    getInitials(firstName, lastName) {
      return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
    },
    getGenderBadgeClass(gender) {
      const classes = {
        male: 'bg-primary-subtle text-primary',
        female: 'bg-pink-subtle text-pink',
        other: 'bg-secondary-subtle text-secondary'
      };
      return classes[gender] || 'bg-secondary-subtle text-secondary';
    },
    formatDate(date) {
      if (!date) return null;
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    resetFilters() {
      this.searchQuery = '';
      this.filterGender = '';
      this.sortBy = 'name';
      this.currentPage = 1;
    },
    resetForm() {
      this.form = {
        username: '',
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        password: '',
        gender: '',
        dob: '',
        blood_group: '',
        address: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        medical_history: ''
      };
    },
    openAddModal() {
      this.isEditing = false;
      this.selectedPatient = null;
      this.resetForm();
      this.modals.edit.show();
    },
    viewPatient(patient) {
      this.selectedPatient = patient;
      this.modals.view.show();
    },
    editPatient(patient) {
      this.isEditing = true;
      this.selectedPatient = patient;
      this.form = {
        first_name: patient.first_name || '',
        last_name: patient.last_name || '',
        email: patient.email || '',
        phone: patient.phone || '',
        username: patient.username || '',
        password: '',
        gender: patient.gender || '',
        dob: patient.dob || '',
        blood_group: patient.blood_group || '',
        address: patient.address || '',
        emergency_contact_name: patient.emergency_contact_name || '',
        emergency_contact_phone: patient.emergency_contact_phone || '',
        medical_history: patient.medical_history || ''
      };
      this.modals.edit.show();
    },
    editFromView() {
      this.modals.view.hide();
      this.editPatient(this.selectedPatient);
    },
    async savePatient() {
      try {
        this.saving = true;
        
        const payload = { ...this.form };
        if (this.isEditing) {
          delete payload.password;
          delete payload.email;
        }

        if (this.isEditing) {
          await api.patch(`/admin/patients/${this.selectedPatient.id}`, payload);
        } else {
          await api.post('/admin/patients', payload);
        }

        this.modals.edit.hide();
        await this.fetchPatients();
      } catch (error) {
        console.error('Failed to save patient:', error);
        alert(error.response?.data?.message || 'Failed to save patient');
      } finally {
        this.saving = false;
      }
    },
    confirmDelete(patient) {
      this.selectedPatient = patient;
      this.modals.delete.show();
    },
    async deletePatient() {
      try {
        this.deleting = true;
        await api.delete(`/admin/patients/${this.selectedPatient.id}`);
        this.modals.delete.hide();
        await this.fetchPatients();
      } catch (error) {
        console.error('Failed to delete patient:', error);
        alert(error.response?.data?.message || 'Failed to delete patient');
      } finally {
        this.deleting = false;
      }
    },
    async viewHistory(patient) {
      this.selectedPatient = patient;
      this.medicalHistory = [];
      this.loadingHistory = true;
      this.modals.history.show();

      try {
        const response = await api.get(`/admin/patients/${patient.id}/history`);
        if (response.data.status === 'success') {
          this.medicalHistory = response.data.data.records;
        }
      } catch (error) {
        console.error('Failed to fetch medical history:', error);
      } finally {
        this.loadingHistory = false;
      }
    }
  },
  mounted() {
    this.fetchPatients();
    
    // Initialize modals
    this.modals = {
      view: new Modal(this.$refs.viewModal),
      edit: new Modal(this.$refs.editModal),
      delete: new Modal(this.$refs.deleteModal),
      history: new Modal(this.$refs.historyModal)
    };
  }
};
</script>

<style scoped>
.avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.avatar-lg {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-pink-subtle {
  background-color: rgba(233, 30, 99, 0.1);
}

.text-pink {
  color: #e91e63;
}
</style>