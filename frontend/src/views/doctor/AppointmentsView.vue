<template>
  <div class="appointments-view">
    <PageHeader 
      title="Appointments" 
      subtitle="Manage your appointments"
    />

    <!-- Filters Card -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label small fw-medium">Start Date</label>
            <input 
              type="date" 
              class="form-control" 
              v-model="filters.start_date"
            >
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-medium">End Date</label>
            <input 
              type="date" 
              class="form-control" 
              v-model="filters.end_date"
            >
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-medium">Status</label>
            <select class="form-select" v-model="filters.status">
              <option value="">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="no_show">No Show</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small fw-medium">Search Patient</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="filters.search"
              placeholder="Patient name..."
            >
          </div>
          <div class="col-md-2">
            <div class="d-flex gap-2">
              <button class="btn btn-success flex-grow-1" @click="fetchAppointments">
                <i class="bi bi-search me-1"></i>Search
              </button>
              <button class="btn btn-outline-secondary" @click="resetFilters" title="Reset">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Filter Tabs -->
    <div class="mb-4">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <button 
            class="nav-link" 
            :class="{ active: activeTab === 'today' }"
            @click="setQuickFilter('today')"
          >
            <i class="bi bi-calendar-day me-1"></i>Today
            <span v-if="counts.today" class="badge bg-white text-success ms-1">{{ counts.today }}</span>
          </button>
        </li>
        <li class="nav-item">
          <button 
            class="nav-link"
            :class="{ active: activeTab === 'upcoming' }"
            @click="setQuickFilter('upcoming')"
          >
            <i class="bi bi-calendar-week me-1"></i>Upcoming
          </button>
        </li>
        <li class="nav-item">
          <button 
            class="nav-link"
            :class="{ active: activeTab === 'past' }"
            @click="setQuickFilter('past')"
          >
            <i class="bi bi-clock-history me-1"></i>Past
          </button>
        </li>
        <li class="nav-item">
          <button 
            class="nav-link"
            :class="{ active: activeTab === 'all' }"
            @click="setQuickFilter('all')"
          >
            <i class="bi bi-list me-1"></i>All
          </button>
        </li>
      </ul>
    </div>

    <!-- Appointments Table -->
    <DataTable
      :title="tableTitle"
      icon="bi bi-calendar-check"
      icon-color="#198754"
      :columns="columns"
      :items="filteredAppointments"
      :loading="loading"
      empty-icon="bi bi-calendar-x"
      empty-message="No appointments found for the selected criteria"
      variant="success"
    >
      <template #header-actions>
        <span class="text-muted small me-3">
          {{ filteredAppointments.length }} appointments
        </span>
      </template>

      <!-- Date Column -->
      <template #cell-appointment_date="{ value }">
        <span class="small">{{ formatDate(value) }}</span>
      </template>

      <!-- Time Column -->
      <template #cell-appointment_time="{ value }">
        <span class="fw-semibold text-success">{{ formatTime(value) }}</span>
      </template>

      <!-- Patient Column -->
      <template #cell-patient_name="{ item }">
        <div class="d-flex align-items-center">
          <div class="avatar-sm bg-primary-subtle rounded-circle me-2">
            <span class="text-primary small fw-bold">{{ getInitials(item.patient_name) }}</span>
          </div>
          <div>
            <div class="fw-medium">{{ item.patient_name }}</div>
            <small class="text-muted">{{ item.booking_notes || 'General Consultation' }}</small>
          </div>
        </div>
      </template>

      <!-- Status Column -->
      <template #cell-status="{ item }">
        <StatusBadge :status="item.status" />
      </template>

      <!-- Actions Column -->
      <template #actions="{ item }">
        <div class="btn-group btn-group-sm">
          <!-- Start Consultation -->
          <button 
            v-if="item.status === 'scheduled' && isToday(item.appointment_date)"
            class="btn btn-success"
            @click="startConsultation(item)"
            title="Start Consultation"
          >
            <i class="bi bi-play-fill"></i>
          </button>

          <!-- View Medical Record -->
          <button 
            v-if="item.status === 'completed'"
            class="btn btn-outline-primary"
            @click="viewMedicalRecord(item)"
            title="View Medical Record"
          >
            <i class="bi bi-file-medical"></i>
          </button>

          <!-- Mark No Show -->
          <button 
            v-if="item.status === 'scheduled'"
            class="btn btn-outline-warning"
            @click="confirmNoShow(item)"
            title="No Show"
          >
            <i class="bi bi-person-x"></i>
          </button>

          <!-- Cancel -->
          <button 
            v-if="item.status === 'scheduled'"
            class="btn btn-outline-danger"
            @click="confirmCancel(item)"
            title="Cancel"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </template>
    </DataTable>

    <!-- Consultation Modal -->
    <ConsultationModal
      ref="consultationModal"
      :appointment="selectedAppointment"
      :loading="submitting"
      @submit="submitConsultation"
      @view-history="viewPatientHistory"
    />

    <!-- Medical Record Modal -->
    <MedicalRecordModal
      ref="medicalRecordModal"
      :record="selectedRecord"
      :show-doctor-notes="true"
    />

    <!-- Confirm No Show Modal -->
    <ConfirmModal
      ref="noShowModal"
      title="Mark as No Show"
      message="Are you sure you want to mark this appointment as No Show?"
      icon="bi bi-person-x"
      variant="warning"
      confirm-text="Yes, No Show"
      :loading="submitting"
      @confirm="handleNoShow"
    />

    <!-- Confirm Cancel Modal -->
    <ConfirmModal
      ref="cancelModal"
      title="Cancel Appointment"
      message="Are you sure you want to cancel this appointment?"
      icon="bi bi-x-circle"
      variant="danger"
      confirm-text="Yes, Cancel"
      :loading="submitting"
      @confirm="handleCancel"
    />
  </div>
</template>

<script>
import api from '@/services/api';

import PageHeader from '@/components/common/PageHeader.vue';
import DataTable from '@/components/common/DataTable.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import MedicalRecordModal from '@/components/medicalRecord/MedicalRecordModal.vue';

import ConsultationModal from '@/components/doctor/ConsultationModal.vue';

export default {
  name: 'AppointmentsView',
  components: {
    PageHeader,
    DataTable,
    StatusBadge,
    ConfirmModal,
    MedicalRecordModal,
    ConsultationModal
  },
  data() {
    return {
      loading: true,
      submitting: false,
      appointments: [],
      selectedAppointment: null,
      selectedRecord: null,
      activeTab: 'today',
      filters: {
        start_date: '',
        end_date: '',
        status: '',
        search: ''
      },
      counts: {
        today: 0
      },
      columns: [
        { key: 'appointment_date', label: 'Date' },
        { key: 'appointment_time', label: 'Time' },
        { key: 'patient_name', label: 'Patient' },
        { key: 'status', label: 'Status' }
      ]
    };
  },
  computed: {
    tableTitle() {
      const titles = {
        today: "Today's Appointments",
        upcoming: 'Upcoming Appointments',
        past: 'Past Appointments',
        all: 'All Appointments'
      };
      return titles[this.activeTab] || 'Appointments';
    },
    filteredAppointments() {
      let result = [...this.appointments];

      if (this.filters.search) {
        const search = this.filters.search.toLowerCase();
        result = result.filter(a => 
          a.patient_name?.toLowerCase().includes(search)
        );
      }

      return result;
    }
  },
  methods: {
    async fetchAppointments() {
      try {
        this.loading = true;
        const params = {};

        if (this.filters.start_date) params.start_date = this.filters.start_date;
        if (this.filters.end_date) params.end_date = this.filters.end_date;
        if (this.filters.status) params.status = this.filters.status;

        const response = await api.get('/doctor/appointments', { params });

        if (response.data.status === 'success') {
          this.appointments = response.data.data.appointments.sort((a, b) => {
            const dateCompare = a.appointment_date.localeCompare(b.appointment_date);
            if (dateCompare !== 0) return dateCompare;
            return a.appointment_time.localeCompare(b.appointment_time);
          });
        }
      } catch (error) {
        console.error('Failed to fetch appointments:', error);
      } finally {
        this.loading = false;
      }
    },

    async fetchTodayCount() {
      try {
        const today = new Date().toISOString().split('T')[0];
        const response = await api.get('/doctor/appointments', {
          params: { start_date: today, end_date: today, status: 'scheduled' }
        });
        if (response.data.status === 'success') {
          this.counts.today = response.data.data.appointments.length;
        }
      } catch (error) {
        console.error('Failed to fetch today count:', error);
      }
    },

    setQuickFilter(tab) {
      this.activeTab = tab;
      const today = new Date().toISOString().split('T')[0];

      switch (tab) {
        case 'today':
          this.filters.start_date = today;
          this.filters.end_date = today;
          this.filters.status = '';
          break;
        case 'upcoming':
          this.filters.start_date = today;
          this.filters.end_date = '';
          this.filters.status = 'scheduled';
          break;
        case 'past':
          this.filters.start_date = '';
          this.filters.end_date = this.getYesterday();
          this.filters.status = '';
          break;
        case 'all':
          this.filters.start_date = '';
          this.filters.end_date = '';
          this.filters.status = '';
          break;
      }

      this.fetchAppointments();
    },

    getYesterday() {
      const d = new Date();
      d.setDate(d.getDate() - 1);
      return d.toISOString().split('T')[0];
    },

    resetFilters() {
      this.filters = { start_date: '', end_date: '', status: '', search: '' };
      this.activeTab = 'all';
      this.fetchAppointments();
    },

    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    },

    formatTime(time) {
      if (!time) return '';
      const [hours, minutes] = time.split(':');
      const h = parseInt(hours);
      return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
    },

    getInitials(name) {
      if (!name) return '?';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },

    isToday(date) {
      return date === new Date().toISOString().split('T')[0];
    },

    // Consultation
    startConsultation(appointment) {
      this.selectedAppointment = appointment;
      this.$refs.consultationModal.show();
    },

    async submitConsultation(formData) {
      try {
        this.submitting = true;
        await api.post(`/doctor/appointments/${this.selectedAppointment.id}/complete`, formData);
        this.$refs.consultationModal.hide();
        await this.fetchAppointments();
        await this.fetchTodayCount();
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to complete consultation');
      } finally {
        this.submitting = false;
      }
    },

    // Medical Record
    async viewMedicalRecord(appointment) {
      try {
        const response = await api.get(`/doctor/appointments/${appointment.id}/record`);
        if (response.data.status === 'success') {
          this.selectedRecord = {
            ...response.data.data.record,
            patient_name: appointment.patient_name,
            doctor_name: appointment.doctor_name
          };
          this.$refs.medicalRecordModal.show();
        }
      } catch (error) {
        alert('Failed to load medical record');
      }
    },

    viewPatientHistory(patientId) {
      this.$router.push(`/doctor/patients/${patientId}`);
    },

    // No Show
    confirmNoShow(appointment) {
      this.selectedAppointment = appointment;
      this.$refs.noShowModal.show();
    },

    async handleNoShow() {
      try {
        this.submitting = true;
        await api.patch(`/doctor/appointments/${this.selectedAppointment.id}/status`, { 
          status: 'no_show' 
        });
        this.$refs.noShowModal.hide();
        await this.fetchAppointments();
        await this.fetchTodayCount();
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update');
      } finally {
        this.submitting = false;
      }
    },

    // Cancel
    confirmCancel(appointment) {
      this.selectedAppointment = appointment;
      this.$refs.cancelModal.show();
    },

    async handleCancel() {
      try {
        this.submitting = true;
        await api.patch(`/doctor/appointments/${this.selectedAppointment.id}/status`, { 
          status: 'cancelled' 
        });
        this.$refs.cancelModal.hide();
        await this.fetchAppointments();
        await this.fetchTodayCount();
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to cancel');
      } finally {
        this.submitting = false;
      }
    }
  },

  mounted() {
    this.setQuickFilter('today');
    this.fetchTodayCount();
  }
};
</script>

<style scoped>
.avatar-sm {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-pills .nav-link {
  color: #6c757d;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  margin-right: 0.5rem;
}

.nav-pills .nav-link.active {
  background-color: #198754;
  color: white;
}

.nav-pills .nav-link:hover:not(.active) {
  background-color: #f8f9fa;
}
</style>