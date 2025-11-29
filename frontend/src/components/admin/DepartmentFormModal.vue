<template>
  <div class="modal fade" ref="modal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header" :class="isEdit ? 'bg-warning-subtle' : 'bg-primary text-white'">
          <h5 class="modal-title">
            <i :class="isEdit ? 'bi bi-pencil' : 'bi bi-plus-lg'" class="me-2"></i>
            {{ isEdit ? 'Edit Department' : 'Add Department' }}
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            :class="{ 'btn-close-white': !isEdit }"
            data-bs-dismiss="modal"
          ></button>
        </div>
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <!-- Department Name -->
            <div class="mb-3">
              <label class="form-label">
                Department Name <span class="text-danger">*</span>
              </label>
              <input 
                type="text" 
                class="form-control" 
                :class="{ 'is-invalid': errors.name }"
                v-model="form.name"
                placeholder="e.g., Cardiology"
                required
              >
              <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
            </div>

            <!-- Description -->
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea 
                class="form-control" 
                v-model="form.description"
                rows="3"
                placeholder="Brief description of the department..."
              ></textarea>
            </div>

            <!-- Status -->
            <div class="mb-3">
              <label class="form-label">Status</label>
              <div class="form-check form-switch">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  v-model="form.is_active"
                  id="deptStatus"
                >
                <label class="form-check-label" for="deptStatus">
                  {{ form.is_active ? 'Active' : 'Inactive' }}
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn"
              :class="isEdit ? 'btn-warning' : 'btn-primary'"
              :disabled="saving"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ isEdit ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/services/api';

export default {
  name: 'DepartmentFormModal',
  emits: ['saved'],
  data() {
    return {
      modal: null,
      saving: false,
      isEdit: false,
      departmentId: null,
      form: {
        name: '',
        description: '',
        is_active: true
      },
      errors: {}
    };
  },
  methods: {
    show(department = null) {
      this.resetForm();
      
      if (department) {
        this.isEdit = true;
        this.departmentId = department.id;
        this.form = {
          name: department.name || '',
          description: department.description || '',
          is_active: department.is_active !== false
        };
      } else {
        this.isEdit = false;
        this.departmentId = null;
      }
      
      this.modal.show();
    },

    hide() {
      this.modal.hide();
    },

    resetForm() {
      this.form = {
        name: '',
        description: '',
        is_active: true
      };
      this.errors = {};
      this.isEdit = false;
      this.departmentId = null;
    },

    validate() {
      this.errors = {};
      
      if (!this.form.name?.trim()) {
        this.errors.name = 'Department name is required';
      } else if (this.form.name.length < 2) {
        this.errors.name = 'Name must be at least 2 characters';
      }

      return Object.keys(this.errors).length === 0;
    },

    async handleSubmit() {
      if (!this.validate()) return;

      try {
        this.saving = true;

        const payload = {
          name: this.form.name.trim(),
          description: this.form.description?.trim() || '',
          is_active: this.form.is_active
        };

        if (this.isEdit) {
          await api.put(`/admin/departments/${this.departmentId}`, payload);
        } else {
          await api.post('/admin/departments', payload);
        }

        this.$emit('saved');
        this.hide();
      } catch (e) {
        console.error('Failed to save department:', e);
        const message = e.response?.data?.message || 'Failed to save department';
        
        if (message.toLowerCase().includes('name') || message.toLowerCase().includes('exists')) {
          this.errors.name = message;
        } else {
          alert(message);
        }
      } finally {
        this.saving = false;
      }
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>