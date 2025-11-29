<template>
  <div class="modal fade" ref="modal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-info text-white">
          <h5 class="modal-title">
            <i class="bi bi-person me-2"></i>Patient Details
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" v-if="patient">
            <!-- <p>{{ patient }}</p> -->
          <!-- profile Header -->
          <div class="text-center mb-4">
            <div class="avatar-circle mx-auto mb-3">
              <span class="avatar-initials">{{ initials }}</span>
            </div>
            <h4 class="fw-semibold mb-1">{{ patient.full_name }}</h4>
            <p class="text-muted mb-0">{{ patient.email }}</p>
          </div>

          <!-- glaceing stats -->
          <div class="row g-3 mb-4">
            <div class="col-4">
              <div class="bg-primary-subtle rounded-3 p-3 text-center">
                <div class="fs-4 fw-bold text-primary">{{ patient.total_appointments || 0 }}</div>
                <small class="text-muted">Appointments</small>
              </div>
            </div>
            <div class="col-4">
              <div class="bg-success-subtle rounded-3 p-3 text-center">
                <div class="fs-4 fw-bold text-success">{{ patient.completed_appointments || 0 }}</div>
                <small class="text-muted">Completed</small>
              </div>
            </div>
            <div class="col-4">
              <div class="bg-info-subtle rounded-3 p-3 text-center">
                <div class="fs-4 fw-bold text-info">{{ patient.medical_records || 0 }}</div>
                <small class="text-muted">Records</small>
              </div>
            </div>
          </div>

          <!-- tabs -->
          <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'info' }"
                @click="activeTab = 'info'"
              >
                <i class="bi bi-person me-1"></i>Information
              </button>
            </li>
          </ul>

          <div class="tab-content p-3">
            <!-- Info Tab -->
            <div v-show="activeTab === 'info'">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="text-muted small">Phone</label>
                  <p class="fw-medium mb-2">{{ patient.phone || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Date of Birth</label>
                  <p class="fw-medium mb-2">{{ formatDate(patient.dob) || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Gender</label>
                  <p class="fw-medium mb-2">{{ formatGender(patient.gender) || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Blood Group</label>
                  <p class="fw-medium mb-2">
                    <span v-if="patient.blood_group" class="badge bg-danger-subtle text-danger">
                      {{ patient.blood_group }}
                    </span>
                    <span v-else>-</span>
                  </p>
                </div>
                <div class="col-12">
                  <label class="text-muted small">Address</label>
                  <p class="fw-medium mb-2">{{ patient.address || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Emergency Contact</label>
                  <p class="fw-medium mb-2">{{ patient.emergency_contact_name || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Emergency Phone</label>
                  <p class="fw-medium mb-2">{{ patient.emergency_contact_phone || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Registered On</label>
                  <p class="fw-medium mb-2">{{ formatDate(patient.created_at) || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Status</label>
                  <p class="mb-2">
                    <span 
                      class="badge"
                      :class="patient.is_active ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'"
                    >
                      {{ patient.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
          <button type="button" class="btn btn-info" @click="viewFullHistory">
            <i class="bi bi-file-medical me-1"></i>Full History
          </button>
          <button type="button" class="btn btn-warning" @click="$emit('edit', patient)">
            <i class="bi bi-pencil me-1"></i>Edit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/services/api';

export default {
  name: 'PatientViewModal',
  emits: ['edit'],
  data() {
    return {
      modal: null,
      patient: null,
      activeTab: 'info',
      loadingHistory: false,
      appointments: []
    };
  },
  computed: {
    initials() {
      if (!this.patient?.full_name) return '?';
      return this.patient.full_name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    }
  },
  methods: {
    show(patient) {
      this.patient = patient;
      this.activeTab = 'info';
      this.appointments = [];
      this.modal.show();
    },

    hide() {
      this.modal.hide();
    },

    async loadHistory() {
      this.activeTab = 'history';
      
      if (this.appointments.length > 0) return;

      try {
        this.loadingHistory = true;
        const res = await api.get(`/admin/patients/${this.patient.id}/appointments`);
        this.appointments = res.data?.data?.appointments || [];
      } catch (e) {
        console.error('Failed to load history:', e);
      } finally {
        this.loadingHistory = false;
      }
    },

    viewFullHistory() {
      this.hide();
      this.$router.push(`/admin/patients/${this.patient.id}`);
    },

    formatDate(date) {
      if (!date) return null;
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    },

    formatGender(gender) {
      if (!gender) return null;
      return gender.charAt(0).toUpperCase() + gender.slice(1);
    },

    formatStatus(status) {
      if (!status) return '';
      return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
    },

    getStatusClass(status) {
      const classes = {
        'scheduled': 'bg-primary-subtle text-primary',
        'completed': 'bg-success-subtle text-success',
        'cancelled': 'bg-danger-subtle text-danger',
        'no_show': 'bg-warning-subtle text-warning'
      };
      return classes[status] || 'bg-secondary-subtle text-secondary';
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>

<style scoped>
.avatar-circle {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-initials {
  color: white;
  font-size: 2rem;
  font-weight: 600;
}

.nav-tabs .nav-link {
  color: #6c757d;
  border: none;
  border-bottom: 2px solid transparent;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom-color: #0d6efd;
  background: transparent;
}
</style>