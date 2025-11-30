<template>
  <div class="department-list-view">
    <PageHeader 
      title="Departments" 
      subtitle="Manage hospital departments and specializations"
    >
      <template #actions>
        <button class="btn btn-primary" @click="openAddModal">
          <i class="bi bi-plus-lg me-2"></i>Add Department
        </button>
      </template>
    </PageHeader>

    <!-- stat cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <StatsCard
          title="Total Departments"
          :value="departments.length"
          icon="bi bi-building"
          variant="primary"
        />
      </div>
      <div class="col-md-4">
        <StatsCard
          title="Active"
          :value="activeDepartments"
          icon="bi bi-check-circle"
          variant="success"
        />
      </div>
      <div class="col-md-4">
        <StatsCard
          title="Inactive"
          :value="inactiveDepartments"
          icon="bi bi-x-circle"
          variant="danger"
        />
      </div>
    </div>

    <!-- filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body py-3">
        <div class="row g-3 align-items-center">
          <div class="col-md-6">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search departments..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-4">
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

<!-- loading state -->
    <LoadingSpinner v-if="loading" message="Loading departments..." />

    <!-- Empty State -->
    <EmptyState 
      v-else-if="filteredDepartments.length === 0"
      icon="bi bi-building"
      :message="emptyMessage"
    >
      <button v-if="!hasFilters" class="btn btn-primary mt-3" @click="openAddModal">
        <i class="bi bi-plus-lg me-2"></i>Add First Department
      </button>
    </EmptyState>

<!-- dept table -->
    <div v-else class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Department</th>
              <th>Description</th>
              <th>Doctors</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dept in filteredDepartments" :key="dept.id">
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar-sm bg-primary-subtle text-primary rounded me-3">
                    <i class="bi bi-building"></i>
                  </div>
                  <div class="fw-semibold">{{ dept.name }}</div>
                </div>
              </td>
              <td>
                <span class="text-muted">
                  {{ truncate(dept.description, 50) || '-' }}
                </span>
              </td>
              <td>
                <span class="badge bg-info-subtle text-info">
                  {{ dept.total_doctors || 0 }} doctors
                </span>
              </td>
              <td>
                <span 
                  class="badge"
                  :class="dept.is_active ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'"
                >
                  <i :class="dept.is_active ? 'bi bi-check-circle' : 'bi bi-x-circle'" class="me-1"></i>
                  {{ dept.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div class="d-flex gap-1">
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="openEditModal(dept)"
                    title="Edit"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDelete(dept)"
                    title="Delete"
                    :disabled="dept.doctor_count > 0"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Form Modal -->
    <DepartmentFormModal 
      ref="formModal"
      @saved="fetchDepartments"
    />

    <!-- Delete Confirmation -->
    <ConfirmModal
      ref="deleteModal"
      title="Delete Department"
      message="Are you sure you want to delete this department? This action cannot be undone."
      confirm-text="Delete"
      confirm-variant="danger"
      :loading="deleting"
      @confirm="deleteDepartment"
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
import DepartmentFormModal from '@/components/admin/DepartmentFormModal.vue';

export default {
  name: 'DepartmentListView',
  components: {
    PageHeader,
    StatsCard,
    LoadingSpinner,
    EmptyState,
    ConfirmModal,
    DepartmentFormModal
  },
  data() {
    return {
      loading: true,
      deleting: false,
      departments: [],
      searchQuery: '',
      filterStatus: '',
      selectedDepartment: null
    };
  },
  computed: {
    activeDepartments() {
      return this.departments.filter(d => d.is_active).length;
    },
    inactiveDepartments() {
      return this.departments.filter(d => !d.is_active).length;
    },
    hasFilters() {
      return this.searchQuery || this.filterStatus;
    },
    filteredDepartments() {
      let result = [...this.departments];


      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        result = result.filter(d => 
          d.name?.toLowerCase().includes(q) ||
          d.description?.toLowerCase().includes(q)
        );
      }


      if (this.filterStatus === 'active') {
        result = result.filter(d => d.is_active);
      } else if (this.filterStatus === 'inactive') {
        result = result.filter(d => !d.is_active);
      }

      return result;
    },
    emptyMessage() {
      if (this.hasFilters) {
        return 'No departments match your search criteria';
      }
      return 'No departments found. Add your first department to get started.';
    }
  },
  methods: {
    async fetchDepartments() {
      try {
        this.loading = true;
        const res = await api.get('/admin/departments');
        this.departments = res.data?.data?.departments || [];
      } catch (e) {
        console.error('Failed to fetch departments:', e);
      } finally {
        this.loading = false;
      }
    },

    truncate(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    },

    clearFilters() {
      this.searchQuery = '';
      this.filterStatus = '';
    },

    openAddModal() {
      this.$refs.formModal.show();
    },

    openEditModal(dept) {
      this.$refs.formModal.show(dept);
    },

    confirmDelete(dept) {
      this.selectedDepartment = dept;
      this.$refs.deleteModal.show();
    },

    async deleteDepartment() {
      if (!this.selectedDepartment) return;

      try {
        this.deleting = true;
        await api.delete(`/admin/departments/${this.selectedDepartment.id}`);
        this.$refs.deleteModal.hide();
        this.fetchDepartments();
      } catch (e) {
        console.error('Failed to delete department:', e);
        alert(e.response?.data?.message || 'Failed to delete department');
      } finally {
        this.deleting = false;
      }
    }
  },
  mounted() {
    this.fetchDepartments();
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
  font-size: 1.2rem;
}
</style>