<template>
  <div class="doctor-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1 fw-bold">
          <i class="bi bi-person-badge me-2 text-primary"></i>Doctors
        </h2>
        <p class="text-muted mb-0">Manage hospital doctors and their schedules</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Add Doctor
      </button>
    </div>

    <!-- Search & Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search doctors..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filterDepartment">
              <option value="">All Departments</option>
              <option 
                v-for="dept in departments" 
                :key="dept.id" 
                :value="dept.id"
              >
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filterAvailability">
              <option value="">All Status</option>
              <option value="available">Available</option>
              <option value="unavailable">Unavailable</option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="sortBy">
              <option value="name">Sort by Name</option>
              <option value="department">Sort by Department</option>
              <option value="experience">Sort by Experience</option>
              <option value="fee">Sort by Fee</option>
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
      <p class="mt-2 text-muted">Loading doctors...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger border-0 shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchDoctors">
        Retry
      </button>
    </div>

    <!-- Doctors List -->
    <div v-else-if="filteredDoctors.length > 0" class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Doctor</th>
              <th>Department</th>
              <th>Specialization</th>
              <th>Experience</th>
              <th>Fee</th>
              <th>Status</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doctor in paginatedDoctors" :key="doctor.id">
              <!-- Doctor Info -->
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar bg-light rounded-circle me-3">
                    <span class="text-primary fw-bold">
                      {{ getInitials(doctor.first_name, doctor.last_name) }}
                    </span>
                  </div>
                  <div>
                    <h6 class="mb-0">Dr. {{ doctor.first_name }} {{ doctor.last_name }}</h6>
                    <small class="text-muted">{{ doctor.phone }}</small>
                  </div>
                </div>
              </td>

              <!-- Department -->
              <td>
                <span class="badge bg-info-subtle text-info">
                  <i class="bi bi-building me-1"></i>
                  {{ doctor.department_name || 'No Department' }}
                </span>
              </td>

              <!-- Specialization -->
              <td>{{ doctor.specialization || '-' }}</td>

              <!-- Experience -->
              <td>{{ doctor.experience_years }} years</td>

              <!-- Fee -->
              <td>₹{{ doctor.consultation_fee }}</td>

              <!-- Availability Status -->
              <td>
                <span 
                  class="badge px-3 py-2"
                  :class="doctor.is_available ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'"
                >
                  <i :class="doctor.is_available ? 'bi bi-check-circle me-1' : 'bi bi-x-circle me-1'"></i>
                  {{ doctor.is_available ? 'Available' : 'Unavailable' }}
                </span>
              </td>

              <!-- Actions -->
              <td class="text-center">
                <button 
                  class="btn btn-sm btn-outline-info me-1"
                  @click="viewDoctor(doctor)"
                  title="View Details"
                >
                  <i class="bi bi-eye"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-primary me-1"
                  @click="editDoctor(doctor)"
                  title="Edit"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-secondary me-1"
                  @click="manageSchedule(doctor)"
                  title="Manage Schedule"
                >
                  <i class="bi bi-clock"></i>
                </button>
                <button 
                    class="btn btn-sm"
                    :class="doctor.is_available ? 'btn-outline-warning' : 'btn-outline-success'"
                    @click="toggleStatus(doctor)"
                    :title="doctor.is_available ? 'Deactivate' : 'Activate'"
                  >
                    <i :class="doctor.is_available ? 'bi bi-person-slash' : 'bi bi-person-check'"></i>
                  </button>
                <button 
                  class="btn btn-sm btn-outline-danger"
                  @click="confirmDelete(doctor)"
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
            Showing {{ paginationStart }} - {{ paginationEnd }} of {{ filteredDoctors.length }} doctors
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
      <div class="mb-4">
        <i class="bi bi-person-badge display-1 text-muted"></i>
      </div>
      <h4>No Doctors Found</h4>
      <p class="text-muted">
        {{ searchQuery ? 'Try adjusting your search criteria' : 'Get started by adding a new doctor' }}
      </p>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Add Doctor
      </button>
    </div>

    <!-- View Doctor Modal -->
    <div class="modal fade" id="viewDoctorModal" tabindex="-1" ref="viewDoctorModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0">
          <div class="modal-header bg-light">
            <h5 class="modal-title">
              <i class="bi bi-person-badge me-2"></i>Doctor Details
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4" v-if="selectedDoctor">
            <div class="row">
              <!-- Left Column -->
              <div class="col-md-6">
                <div class="mb-4">
                  <div class="d-flex align-items-center mb-3">
                    <div class="avatar-lg bg-light rounded-circle me-3">
                      <span class="text-primary fw-bold fs-4">
                        {{ getInitials(selectedDoctor.first_name, selectedDoctor.last_name) }}
                      </span>
                    </div>
                    <div>
                      <h4 class="mb-0">Dr. {{ selectedDoctor.first_name }} {{ selectedDoctor.last_name }}</h4>
                      <span 
                        class="badge"
                        :class="selectedDoctor.is_available ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'"
                      >
                        {{ selectedDoctor.is_available ? 'Available' : 'Unavailable' }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="text-muted small">Phone</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-telephone me-2 text-primary"></i>{{ selectedDoctor.phone }}
                  </p>
                </div>

                <div class="mb-3">
                  <label class="text-muted small">Email</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-envelope me-2 text-primary"></i>{{ selectedDoctor.email || 'N/A' }}
                  </p>
                </div>

                <div class="mb-3">
                  <label class="text-muted small">Department</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-building me-2 text-primary"></i>{{ selectedDoctor.department_name || 'N/A' }}
                  </p>
                </div>
              </div>

              <!-- Right Column -->
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="text-muted small">Specialization</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-award me-2 text-primary"></i>{{ selectedDoctor.specialization || 'N/A' }}
                  </p>
                </div>

                <div class="mb-3">
                  <label class="text-muted small">Qualification</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-mortarboard me-2 text-primary"></i>{{ selectedDoctor.qualification || 'N/A' }}
                  </p>
                </div>

                <div class="mb-3">
                  <label class="text-muted small">Experience</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-briefcase me-2 text-primary"></i>{{ selectedDoctor.experience_years }} years
                  </p>
                </div>

                <div class="mb-3">
                  <label class="text-muted small">Consultation Fee</label>
                  <p class="mb-0 fw-medium">
                    <i class="bi bi-currency-rupee me-2 text-primary"></i>₹{{ selectedDoctor.consultation_fee }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="editDoctorFromView">
              <i class="bi bi-pencil me-2"></i>Edit Doctor
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Doctor Modal -->
    <div class="modal fade" id="doctorModal" tabindex="-1" ref="doctorModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0">
          <div class="modal-header bg-light">
            <h5 class="modal-title">
              <i class="bi bi-person-badge me-2"></i>
              {{ isEditing ? 'Edit Doctor' : 'Add New Doctor' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveDoctor">
            <div class="modal-body p-4">
              <!-- Account Info (only for new doctor) -->
              <div v-if="!isEditing" class="mb-4">
                <h6 class="text-muted mb-3 border-bottom pb-2">
                  <i class="bi bi-person-lock me-2"></i>Account Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-4">
                    <label class="form-label">Username <span class="text-danger">*</span></label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="form.username"
                      :class="{ 'is-invalid': formErrors.username }"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.username }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Email <span class="text-danger">*</span></label>
                    <input 
                      type="email" 
                      class="form-control" 
                      v-model="form.email"
                      :class="{ 'is-invalid': formErrors.email }"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.email }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Password <span class="text-danger">*</span></label>
                    <input 
                      type="password" 
                      class="form-control" 
                      v-model="form.password"
                      :class="{ 'is-invalid': formErrors.password }"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.password }}</div>
                  </div>
                </div>
              </div>

              <!-- Personal Info -->
              <div class="mb-4">
                <h6 class="text-muted mb-3 border-bottom pb-2">
                  <i class="bi bi-person me-2"></i>Personal Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-4">
                    <label class="form-label">First Name <span class="text-danger">*</span></label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="form.first_name"
                      :class="{ 'is-invalid': formErrors.first_name }"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.first_name }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Last Name <span class="text-danger">*</span></label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="form.last_name"
                      :class="{ 'is-invalid': formErrors.last_name }"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.last_name }}</div>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">Phone <span class="text-danger">*</span></label>
                    <input 
                      type="tel" 
                      class="form-control" 
                      v-model="form.phone"
                      :class="{ 'is-invalid': formErrors.phone }"
                      pattern="[0-9]{10}"
                      placeholder="10-digit number"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.phone }}</div>
                  </div>
                </div>
              </div>

              <!-- Professional Info -->
              <div class="mb-4">
                <h6 class="text-muted mb-3 border-bottom pb-2">
                  <i class="bi bi-briefcase me-2"></i>Professional Information
                </h6>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Department <span class="text-danger">*</span></label>
                    <select 
                      class="form-select" 
                      v-model="form.department_id"
                      :class="{ 'is-invalid': formErrors.department_id }"
                      required
                    >
                      <option value="">Select Department</option>
                      <option 
                        v-for="dept in departments" 
                        :key="dept.id" 
                        :value="dept.id"
                      >
                        {{ dept.name }}
                      </option>
                    </select>
                    <div class="invalid-feedback">{{ formErrors.department_id }}</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Specialization <span class="text-danger">*</span></label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="form.specialization"
                      :class="{ 'is-invalid': formErrors.specialization }"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.specialization }}</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Qualification <span class="text-danger">*</span></label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="form.qualification"
                      :class="{ 'is-invalid': formErrors.qualification }"
                      placeholder="e.g., MBBS, MD"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.qualification }}</div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Experience (Years) <span class="text-danger">*</span></label>
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model.number="form.experience_years"
                      :class="{ 'is-invalid': formErrors.experience_years }"
                      min="0"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.experience_years }}</div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Consultation Fee (₹) <span class="text-danger">*</span></label>
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model.number="form.consultation_fee"
                      :class="{ 'is-invalid': formErrors.consultation_fee }"
                      min="0"
                      required
                    >
                    <div class="invalid-feedback">{{ formErrors.consultation_fee }}</div>
                  </div>
                </div>
              </div>

              <!-- Status (only for edit) -->
              <div v-if="isEditing" class="form-check form-switch">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="isAvailable"
                  v-model="form.is_available"
                >
                <label class="form-check-label" for="isAvailable">Available for appointments</label>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ isEditing ? 'Update Doctor' : 'Create Doctor' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Schedule Modal -->
    <div class="modal fade" id="scheduleModal" tabindex="-1" ref="scheduleModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0">
          <div class="modal-header bg-light">
            <h5 class="modal-title">
              <i class="bi bi-clock me-2"></i>
              Working Hours - Dr. {{ selectedDoctor?.first_name }} {{ selectedDoctor?.last_name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <div v-if="loadingSchedule" class="text-center py-4">
              <div class="spinner-border text-primary"></div>
              <p class="mt-2 text-muted">Loading schedule...</p>
            </div>
            <div v-else>
              <p class="text-muted mb-4">Set the working hours for each day of the week.</p>
              <div 
                v-for="(day, index) in scheduleForm" 
                :key="index"
                class="row g-3 mb-3 align-items-center py-2 border-bottom"
              >
                <div class="col-md-3">
                  <div class="form-check form-switch">
                    <input 
                      type="checkbox" 
                      class="form-check-input" 
                      :id="'day-' + index"
                      v-model="day.is_active"
                    >
                    <label 
                      class="form-check-label fw-medium" 
                      :for="'day-' + index"
                      :class="{ 'text-muted': !day.is_active }"
                    >
                      {{ dayNames[index] }}
                    </label>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">From</span>
                    <input 
                      type="time" 
                      class="form-control" 
                      v-model="day.start_time"
                      :disabled="!day.is_active"
                    >
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">To</span>
                    <input 
                      type="time" 
                      class="form-control" 
                      v-model="day.end_time"
                      :disabled="!day.is_active"
                    >
                  </div>
                </div>
                <div class="col-md-1 text-center">
                  <i 
                    class="bi"
                    :class="day.is_active ? 'bi-check-circle-fill text-success' : 'bi-x-circle text-muted'"
                  ></i>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveSchedule"
              :disabled="savingSchedule"
            >
              <span v-if="savingSchedule" class="spinner-border spinner-border-sm me-2"></span>
              Save Schedule
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content border-0">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle me-2"></i>Confirm Delete
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <p>Are you sure you want to delete <strong>Dr. {{ selectedDoctor?.first_name }} {{ selectedDoctor?.last_name }}</strong>?</p>
            <div class="alert alert-warning mb-0">
              <i class="bi bi-info-circle me-2"></i>
              This will also delete the associated user account. This action cannot be undone.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteDoctor"
              :disabled="deleting"
            >
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              Delete Doctor
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/services/api';

export default {
  name: 'DoctorListView',
  data() {
    return {
      doctors: [],
      departments: [],
      loading: false,
      error: null,
      searchQuery: '',
      filterDepartment: '',
      filterAvailability: '',
      sortBy: 'name',
      currentPage: 1,
      perPage: 10,

      // Modal state
      isEditing: false,
      saving: false,
      deleting: false,
      selectedDoctor: null,

      // Form
      form: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        phone: '',
        department_id: '',
        specialization: '',
        qualification: '',
        experience_years: 0,
        consultation_fee: 0,
        is_available: true
      },
      formErrors: {},

      // Schedule
      loadingSchedule: false,
      savingSchedule: false,
      hasExistingSchedule: false,
      scheduleForm: [],
      dayNames: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],

      // Bootstrap modals
      viewDoctorModalInstance: null,
      doctorModalInstance: null,
      deleteModalInstance: null,
      scheduleModalInstance: null
    };
  },
  computed: {
    filteredDoctors() {
      let result = [...this.doctors];

      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(doc =>
          doc.first_name?.toLowerCase().includes(query) ||
          doc.last_name?.toLowerCase().includes(query) ||
          doc.specialization?.toLowerCase().includes(query) ||
          doc.phone?.includes(query)
        );
      }

      // Department filter
      if (this.filterDepartment) {
        result = result.filter(doc => doc.department_id === this.filterDepartment);
      }

      // Availability filter
      if (this.filterAvailability) {
        const isAvailable = this.filterAvailability === 'available';
        result = result.filter(doc => doc.is_available === isAvailable);
      }

      // Sorting
      result.sort((a, b) => {
        switch (this.sortBy) {
          case 'name':
            return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`);
          case 'department':
            return (a.department_name || '').localeCompare(b.department_name || '');
          case 'experience':
            return b.experience_years - a.experience_years;
          case 'fee':
            return b.consultation_fee - a.consultation_fee;
          default:
            return 0;
        }
      });

      return result;
    },
    paginatedDoctors() {
      const start = (this.currentPage - 1) * this.perPage;
      const end = start + this.perPage;
      return this.filteredDoctors.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredDoctors.length / this.perPage) || 1;
    },
    paginationStart() {
      return (this.currentPage - 1) * this.perPage + 1;
    },
    paginationEnd() {
      const end = this.currentPage * this.perPage;
      return end > this.filteredDoctors.length ? this.filteredDoctors.length : end;
    }
  },
  watch: {
    filteredDoctors() {
      // Reset to first page when filters change
      this.currentPage = 1;
    }
  },
  mounted() {
    this.fetchDoctors();
    this.fetchDepartments();
    this.initModals();
  },
  beforeUnmount() {
    this.viewDoctorModalInstance?.dispose();
    this.doctorModalInstance?.dispose();
    this.deleteModalInstance?.dispose();
    this.scheduleModalInstance?.dispose();
  },
  methods: {
    initModals() {
      this.viewDoctorModalInstance = new Modal(this.$refs.viewDoctorModal);
      this.doctorModalInstance = new Modal(this.$refs.doctorModal);
      this.deleteModalInstance = new Modal(this.$refs.deleteModal);
      this.scheduleModalInstance = new Modal(this.$refs.scheduleModal);
    },

    async fetchDoctors() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/admin/doctors');
        this.doctors = response.data.data?.doctors || [];
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch doctors';
        console.error('Error fetching doctors:', err);
      } finally {
        this.loading = false;
      }
    },

    async fetchDepartments() {
      try {
        const response = await api.get('/admin/departments');
        this.departments = response.data.data?.departments || [];
      } catch (err) {
        console.error('Error fetching departments:', err);
      }
    },

    resetFilters() {
      this.searchQuery = '';
      this.filterDepartment = '';
      this.filterAvailability = '';
      this.sortBy = 'name';
      this.currentPage = 1;
    },

    getInitials(firstName, lastName) {
      return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
    },

    // View Doctor
    viewDoctor(doctor) {
      this.selectedDoctor = doctor;
      this.viewDoctorModalInstance.show();
    },

    editDoctorFromView() {
      this.viewDoctorModalInstance.hide();
      this.editDoctor(this.selectedDoctor);
    },

    // Add Doctor
    openAddModal() {
      this.isEditing = false;
      this.form = {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        phone: '',
        department_id: '',
        specialization: '',
        qualification: '',
        experience_years: 0,
        consultation_fee: 0,
        is_available: true
      };
      this.formErrors = {};
      this.doctorModalInstance.show();
    },

    // Edit Doctor
    editDoctor(doctor) {
      this.isEditing = true;
      this.selectedDoctor = doctor;
      this.form = {
        first_name: doctor.first_name,
        last_name: doctor.last_name,
        phone: doctor.phone,
        department_id: doctor.department_id,
        specialization: doctor.specialization,
        qualification: doctor.qualification,
        experience_years: doctor.experience_years,
        consultation_fee: doctor.consultation_fee,
        is_available: doctor.is_available
      };
      this.formErrors = {};
      this.doctorModalInstance.show();
    },

    // Save Doctor (Create/Update)
    async saveDoctor() {
      this.formErrors = {};
      this.saving = true;
      console.log('Saving doctor with data:', this.form);

      try {
        if (this.isEditing) {
          await api.patch(`/admin/doctors/${this.selectedDoctor.id}`, this.form);
          this.$toast?.success('Doctor updated successfully');
        } else {
          await api.post('/admin/doctors', this.form);
          this.$toast?.success('Doctor created successfully');
        }

        this.doctorModalInstance.hide();
        this.fetchDoctors();
      } catch (err) {
        const message = err.response?.data?.message || 'Failed to save doctor';
        this.$toast?.error(message);
        console.error('Error saving doctor:', err);

        // Handle validation errors
        if (err.response?.data?.errors) {
          err.response.data.errors.forEach(e => {
            if (e.loc && e.loc.length > 0) {
              this.formErrors[e.loc[e.loc.length - 1]] = e.msg;
            }
          });
        }
      } finally {
        this.saving = false;
      }
    },

    // Manage Schedule
    async manageSchedule(doctor) {
      this.selectedDoctor = doctor;
      this.loadingSchedule = true;
      this.hasExistingSchedule = false;
      this.scheduleModalInstance.show();

      // Initialize empty schedule
      this.scheduleForm = Array(7).fill(null).map((_, i) => ({
        day_of_week: i,
        start_time: '09:00',
        end_time: '17:00',
        is_active: false
      }));

      try {
        const response = await api.get(`/admin/doctors/${doctor.id}/working-hours`);
        const workingHours = response.data.data?.working_hours || [];
        
        if (workingHours.length > 0) {
          this.hasExistingSchedule = true;
          // Map existing working hours
          workingHours.forEach(wh => {
            this.scheduleForm[wh.day_of_week] = {
              day_of_week: wh.day_of_week,
              start_time: wh.start_time,
              end_time: wh.end_time,
              is_active: true
            };
          });
        }
      } catch (err) {
        console.error('Error fetching working hours:', err);
      } finally {
        this.loadingSchedule = false;
      }
    },

    // Save Schedule
    async saveSchedule() {
      this.savingSchedule = true;

      const schedule = this.scheduleForm
        .filter(day => day.is_active)
        .map(day => ({
          day_of_week: day.day_of_week,
          start_time: day.start_time,
          end_time: day.end_time,
          is_active: true
        }));

      try {
        if (this.hasExistingSchedule) {
          await api.put(`/admin/doctors/${this.selectedDoctor.id}/working-hours`, { schedule });
        } else {
          await api.post(`/admin/doctors/${this.selectedDoctor.id}/working-hours`, { schedule });
        }

        this.$toast?.success('Schedule saved successfully');
        this.scheduleModalInstance.hide();
      } catch (err) {
        const message = err.response?.data?.message || 'Failed to save schedule';
        this.$toast?.error(message);
        console.error('Error saving schedule:', err);
      } finally {
        this.savingSchedule = false;
      }
    },

    // Delete Doctor
    confirmDelete(doctor) {
      this.selectedDoctor = doctor;
      this.deleteModalInstance.show();
    },

    async deleteDoctor() {
      this.deleting = true;
      try {
        await api.delete(`/admin/doctors/${this.selectedDoctor.id}`);
        this.$toast?.success('Doctor deleted successfully');
        this.deleteModalInstance.hide();
        this.fetchDoctors();
      } catch (err) {
        const message = err.response?.data?.message || 'Failed to delete doctor';
        this.$toast?.error(message);
        console.error('Error deleting doctor:', err);
      } finally {
        this.deleting = false;
      }
    },

    async toggleStatus(doctor) {
      const action = doctor.is_available ? 'blacklist' : 'activate';
      if (!confirm(`Are you sure you want to ${action} this doctor?`)) return;

      try {
        // First get the user_id for this doctor
        const response = await api.get(`/admin/doctors/${doctor.id}`);
        const userId = response.data.data.doctor.user_id;
        
        await api.patch(`/admin/users/${userId}/status`);
        this.fetchDoctors();
      } catch (e) {
        console.error('Failed to toggle status:', e);
        alert(e.response?.data?.message || 'Failed to update status');
      }
    }
  }
};
</script>

