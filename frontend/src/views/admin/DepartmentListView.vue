<template>
  <div class="department-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1 fw-semibold">
          <i class="bi bi-building me-2 text-primary"></i>Departments
        </h2>
        <p class="text-muted mb-0">Manage hospital departments</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Add Department
      </button>
    </div>

    <!-- Search Bar -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body py-3">
        <div class="row g-3 align-items-center">
          <div class="col-md-6">
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0 bg-light" 
                placeholder="Search departments..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-4">
            <select class="form-select bg-light" v-model="filterStatus">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
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
      <p class="mt-3 text-muted">Loading departments...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger border-0 shadow-sm" role="alert">
      <div class="d-flex align-items-center">
        <i class="bi bi-exclamation-triangle me-2 fs-5"></i>
        <span>{{ error }}</span>
        <button class="btn btn-sm btn-outline-danger ms-auto" @click="fetchDepartments">
          <i class="bi bi-arrow-clockwise me-1"></i>Retry
        </button>
      </div>
    </div>

    <!-- Departments Grid -->
    <div v-else-if="filteredDepartments.length > 0" class="row g-4">
      <div 
        v-for="dept in filteredDepartments" 
        :key="dept.id" 
        class="col-md-6 col-lg-4"
      >
        <div class="card h-100 border-0 shadow-sm department-card">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div 
                class="department-icon rounded-3 p-3"
                :class="dept.is_active ? 'bg-primary-subtle' : 'bg-secondary-subtle'"
              >
                <i 
                  class="bi bi-hospital fs-4"
                  :class="dept.is_active ? 'text-primary' : 'text-secondary'"
                ></i>
              </div>
                            <div class="btn-group">
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="viewDepartment(dept)"
                  title="View Details"
                >
                  <i class="bi bi-eye"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-warning"
                  @click="editDepartment(dept)"
                  title="Edit"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline-danger"
                  @click="confirmDelete(dept)"
                  title="Delete"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>

            <h5 class="card-title mb-2 fw-semibold">{{ dept.name }}</h5>
            <p class="card-text text-muted small mb-3 description-text">
              {{ dept.description || 'No description available' }}
            </p>

            <div class="d-flex justify-content-between align-items-center pt-2 border-top">
              <span class="badge bg-info-subtle text-info px-3 py-2">
                <i class="bi bi-person-badge me-1"></i>
                {{ dept.total_doctors || 0 }} Doctors
              </span>
              <span 
                class="badge px-3 py-2"
                :class="dept.is_active ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'"
              >
                <i :class="dept.is_active ? 'bi bi-check-circle me-1' : 'bi bi-x-circle me-1'"></i>
                {{ dept.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <div class="empty-state-icon mb-4">
        <i class="bi bi-building display-1 text-muted opacity-50"></i>
      </div>
      <h4 class="fw-semibold text-muted">No Departments Found</h4>
      <p class="text-muted mb-4">
        {{ searchQuery ? 'Try adjusting your search criteria' : 'Get started by adding a new department' }}
      </p>
      <button class="btn btn-primary px-4" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Add Department
      </button>
    </div>

    <!-- View Details Modal -->
    <div class="modal fade" id="viewModal" tabindex="-1" ref="viewModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0 pb-0">
            <div class="d-flex align-items-center">
              <div class="icon-box bg-primary-subtle rounded-3 p-3 me-3">
                <i class="bi bi-hospital fs-4 text-primary"></i>
              </div>
              <div>
                <h5 class="modal-title fw-semibold mb-0">{{ selectedDepartment?.name }}</h5>
                <span 
                  class="badge mt-1"
                  :class="selectedDepartment?.is_active ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'"
                >
                  {{ selectedDepartment?.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body pt-4">
            <div class="mb-4">
              <label class="form-label text-muted small fw-semibold text-uppercase">Description</label>
              <p class="mb-0">{{ selectedDepartment?.description || 'No description available' }}</p>
            </div>
            
            <div class="row g-3">
              <div class="col-6">
                <div class="stat-card bg-light rounded-3 p-3 text-center">
                  <i class="bi bi-person-badge fs-4 text-primary mb-2 d-block"></i>
                  <h4 class="fw-bold mb-0">{{ selectedDepartment?.total_doctors || 0 }}</h4>
                  <small class="text-muted">Doctors</small>
                </div>
              </div>
              <div class="col-6">
                <div class="stat-card bg-light rounded-3 p-3 text-center">
                  <i class="bi bi-calendar-check fs-4 text-success mb-2 d-block"></i>
                  <h4 class="fw-bold mb-0">{{ selectedDepartment?.appointment_count || 0 }}</h4>
                  <small class="text-muted">Appointments</small>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="editFromView">
              <i class="bi bi-pencil me-2"></i>Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal fade" id="departmentModal" tabindex="-1" ref="departmentModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-semibold">
              <i :class="isEditing ? 'bi bi-pencil me-2' : 'bi bi-plus-circle me-2'" class="text-primary"></i>
              {{ isEditing ? 'Edit Department' : 'Add New Department' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveDepartment">
            <div class="modal-body">
              <div class="mb-4">
                <label class="form-label fw-semibold">
                  Department Name <span class="text-danger">*</span>
                </label>
                <input 
                  type="text" 
                  class="form-control form-control-lg bg-light border-0" 
                  v-model="form.name"
                  :class="{ 'is-invalid': formErrors.name }"
                  placeholder="Enter department name"
                  required
                >
                <div class="invalid-feedback">{{ formErrors.name }}</div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-semibold">Description</label>
                <textarea 
                  class="form-control bg-light border-0" 
                  rows="4"
                  v-model="form.description"
                  placeholder="Enter department description..."
                ></textarea>
              </div>

              <div class="form-check form-switch" v-if="isEditing">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="isActive"
                  v-model="form.is_active"
                  role="switch"
                >
                <label class="form-check-label fw-semibold" for="isActive">
                  Department is Active
                </label>
              </div>
            </div>
            <div class="modal-footer border-0">
              <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary px-4" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else :class="isEditing ? 'bi bi-check-lg me-2' : 'bi bi-plus-lg me-2'"></i>
                {{ isEditing ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content border-0 shadow">
          <div class="modal-body text-center p-4">
            <div class="delete-icon bg-danger-subtle rounded-circle p-3 d-inline-flex mb-3">
              <i class="bi bi-trash fs-3 text-danger"></i>
            </div>
            <h5 class="fw-semibold mb-2">Delete Department?</h5>
            <p class="text-muted mb-0">
              Are you sure you want to delete <strong>{{ selectedDepartment?.name }}</strong>? 
              This action cannot be undone.
            </p>
          </div>
          <div class="modal-footer border-0 justify-content-center pb-4">
            <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger px-4" 
              @click="deleteDepartment"
              :disabled="deleting"
            >
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-trash me-2"></i>
              Delete
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
  name: 'DepartmentListView',
  data() {
    return {
      departments: [],
      loading: false,
      error: null,
      searchQuery: '',
      filterStatus: '',
      
      // Modal state
      isEditing: false,
      saving: false,
      deleting: false,
      selectedDepartment: null,
      
      // Form
      form: {
        name: '',
        description: '',
        is_active: true
      },
      formErrors: {},
      
      // Bootstrap modals
      departmentModalInstance: null,
      deleteModalInstance: null,
      viewModalInstance: null
    };
  },
  computed: {
    filteredDepartments() {
      let result = this.departments;
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(dept => 
          dept.name.toLowerCase().includes(query) ||
          (dept.description && dept.description.toLowerCase().includes(query))
        );
      }
      
      if (this.filterStatus) {
        const isActive = this.filterStatus === 'active';
        result = result.filter(dept => dept.is_active === isActive);
      }
      
      return result;
    }
  },
  mounted() {
    this.fetchDepartments();
    this.$nextTick(() => {
      this.initModals();
    });
  },
  beforeUnmount() {
    // Clean up modals
    this.departmentModalInstance?.dispose();
    this.deleteModalInstance?.dispose();
    this.viewModalInstance?.dispose();
  },
  methods: {
    initModals() {
      if (this.$refs.departmentModal) {
        this.departmentModalInstance = new Modal(this.$refs.departmentModal);
      }
      if (this.$refs.deleteModal) {
        this.deleteModalInstance = new Modal(this.$refs.deleteModal);
      }
      if (this.$refs.viewModal) {
        this.viewModalInstance = new Modal(this.$refs.viewModal);
      }
    },

    async fetchDepartments() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/admin/departments');
        this.departments = response.data.data?.departments || [];
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to fetch departments';
        console.error('Error fetching departments:', err);
      } finally {
        this.loading = false;
      }
    },

    resetFilters() {
      this.searchQuery = '';
      this.filterStatus = '';
    },

    openAddModal() {
      this.isEditing = false;
      this.form = {
        name: '',
        description: '',
        is_active: true
      };
      this.formErrors = {};
      this.departmentModalInstance?.show();
    },

    viewDepartment(dept) {
      this.selectedDepartment = dept;
      this.viewModalInstance?.show();
    },

    editFromView() {
      this.viewModalInstance?.hide();
      setTimeout(() => {
        this.editDepartment(this.selectedDepartment);
      }, 200);
    },

    editDepartment(dept) {
      this.isEditing = true;
      this.selectedDepartment = dept;
      this.form = {
        name: dept.name,
        description: dept.description || '',
        is_active: dept.is_active !== false
      };
      this.formErrors = {};
      this.departmentModalInstance?.show();
    },

    async saveDepartment() {
    // console.log('Payload:', this.form);
    console.log(api.defaults)
      this.formErrors = {};
      
      if (!this.form.name?.trim()) {
        this.formErrors.name = 'Department name is required';
        return;
      }

      this.saving = true;
      try {
        if (this.isEditing) {
          await api.patch(`/admin/departments/${this.selectedDepartment.id}`, this.form);
        } else {
          await api.post('/admin/departments', this.form);
        }
        
        this.departmentModalInstance?.hide();
        await this.fetchDepartments();
      } catch (err) {
        const message = err.response?.data?.message || 'Failed to save department';
        this.formErrors.name = message;
        console.error('Error saving department:', err);
      } finally {
        this.saving = false;
      }
    },

    confirmDelete(dept) {
      this.selectedDepartment = dept;
      this.deleteModalInstance?.show();
    },

    async deleteDepartment() {
      this.deleting = true;
      try {
        await api.delete(`/admin/departments/${this.selectedDepartment.id}`);
        this.deleteModalInstance?.hide();
        await this.fetchDepartments();
      } catch (err) {
        const message = err.response?.data?.message || 'Failed to delete department';
        console.error('Error deleting department:', err);
        alert(message);
      } finally {
        this.deleting = false;
      }
    }
  }
};
</script>
