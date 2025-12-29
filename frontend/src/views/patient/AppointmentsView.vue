<template>
  <div class="appointments-view">
    <PageHeader title="My Appointments" subtitle="View and manage your appointments">
      <template #actions>
        <router-link to="/patient/doctors" class="btn btn-primary">
          <i class="bi bi-plus-lg me-2"></i>Book Appointment
        </router-link>
      </template>
    </PageHeader>

    <!-- Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body py-3">
        <div class="btn-group" role="group">
          <button 
            v-for="tab in tabs" 
            :key="tab.value"
            type="button" 
            class="btn"
            :class="activeTab === tab.value ? 'btn-primary' : 'btn-outline-primary'"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
            <span class="badge bg-white text-primary ms-1">{{ getCount(tab.value) }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <!-- Empty State -->
    <EmptyState 
      v-else-if="filteredAppointments.length === 0"
      icon="bi bi-calendar-x"
      :message="emptyMessage"
    >
      <router-link to="/patient/doctors" class="btn btn-primary mt-3">
        <i class="bi bi-search me-2"></i>Find a Doctor
      </router-link>
    </EmptyState>

    <!-- Table -->
    <div v-else class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Date & Time</th>
              <th>Doctor</th>
              <th>Status</th>
              <th>Fee</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredAppointments" :key="row.id">
              <!-- Date Column -->
              <td>
                <div class="d-flex align-items-center">
                  <div class="bg-primary-subtle text-primary rounded px-2 py-1 me-2 text-center" style="min-width: 50px;">
                    <div class="fw-bold">{{ getDayOfMonth(row.appointment_date) }}</div>
                    <small>{{ getMonth(row.appointment_date) }}</small>
                  </div>
                  <span class="text-muted">{{ formatTime(row.appointment_time) }}</span>
                </div>
              </td>

              <!-- Doctor Column -->
              <td>
                <div class="fw-medium">{{ row.doctor_name }}</div>
                <small class="text-muted">{{ row.department_name }}</small>
              </td>

              <!-- Status Column -->
              <td>
                <span class="badge" :class="getStatusClass(row.status)">
                  <i :class="getStatusIcon(row.status)" class="me-1"></i>
                  {{ formatStatus(row.status) }}
                </span>
              </td>

              <!-- Fee Column -->
              <td>
                <span v-if="row.consultation_fee" class="text-success fw-medium">
                  ₹{{ row.consultation_fee }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>

              <!-- Actions Column -->
              <td>
                <div class="d-flex gap-1">
                  <!-- Upcoming: Reschedule, Edit Notes & Cancel -->
                  <template v-if="isUpcoming(row)">
                    <button 
                      class="btn btn-sm btn-outline-secondary" 
                      @click="openEditNotes(row)"
                      title="Edit Notes"
                    >
                      <i class="bi bi-chat-left-text"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-primary" 
                      @click="openReschedule(row)"
                      title="Reschedule"
                    >
                      <i class="bi bi-calendar-event"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger" 
                      @click="confirmCancel(row)"
                      title="Cancel"
                    >
                      <i class="bi bi-x-lg"></i>
                    </button>
                  </template>
                  
                  <!-- Completed: View Record -->
                  <template v-else-if="row.status === 'completed'">
                    <button 
                      class="btn btn-sm btn-outline-info" 
                      @click="viewRecord(row)"
                      title="View Medical Record"
                    >
                      <i class="bi bi-file-medical"></i>
                    </button>
                  </template>

                  <!-- Other statuses -->
                  <span v-else class="text-muted small">-</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cancel Confirmation Modal -->
    <ConfirmModal
      ref="cancelModal"
      title="Cancel Appointment"
      message="Are you sure you want to cancel this appointment? This action cannot be undone."
      confirm-text="Yes, Cancel"
      confirm-variant="danger"
      :loading="cancelling"
      @confirm="cancelAppointment"
    />

    <!-- Reschedule Modal -->
    <RescheduleModal
      ref="rescheduleModal"
      :appointment="selectedAppointment"
      @rescheduled="onRescheduled"
    />

    <!-- Medical Record Modal -->
    <MedicalRecordModal
      ref="recordModal"
      :record="selectedRecord"
      modal-id="patientRecordModal"
    />

    <!-- Edit Notes Modal -->
    <div class="modal fade" ref="notesModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-chat-left-text me-2 text-primary"></i>Edit Booking Notes
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-3">
              Add notes for the doctor about your symptoms or concerns.
            </p>
            <textarea 
              class="form-control" 
              v-model="editingNotes"
              rows="4"
              placeholder="Describe your symptoms, concerns, or any information you want the doctor to know..."
            ></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveNotes"
              :disabled="savingNotes"
            >
              <span v-if="savingNotes" class="spinner-border spinner-border-sm me-1"></span>
              Save Notes
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Modal for Record -->
    <div class="modal fade" ref="loadingModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content border-0">
          <div class="modal-body text-center py-4">
            <div class="spinner-border text-primary mb-3"></div>
            <p class="mb-0 text-muted">Loading record...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- No Record Modal -->
    <div class="modal fade" ref="noRecordModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0">
          <div class="modal-body text-center py-5">
            <i class="bi bi-file-earmark-x text-muted" style="font-size: 4rem;"></i>
            <h5 class="mt-3">No Medical Record</h5>
            <p class="text-muted">No medical record has been created for this appointment yet.</p>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">OK</button>
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
import EmptyState from '@/components/common/EmptyState.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import RescheduleModal from '@/components/patient/RescheduleModal.vue';
import MedicalRecordModal from '@/components/medicalRecord/MedicalRecordModal.vue';

export default {
  name: 'AppointmentsView',
  components: { 
    PageHeader, EmptyState, ConfirmModal,
    RescheduleModal, MedicalRecordModal
  },
  data() {
    return {
      loading: true,
      appointments: [],
      activeTab: 'upcoming',
      selectedAppointment: null,
      selectedRecord: null,
      cancelling: false,
      loadingModal: null,
      noRecordModal: null,
      notesModal: null,
      editingNotes: '',
      savingNotes: false,
      tabs: [
        { label: 'Upcoming', value: 'upcoming' },
        { label: 'Completed', value: 'completed' },
        { label: 'Cancelled', value: 'cancelled' },
        { label: 'All', value: 'all' }
      ]
    };
  },
  computed: {
    filteredAppointments() {
      let result = [...this.appointments];
      const today = new Date().toISOString().split('T')[0];

      if (this.activeTab === 'upcoming') {
        result = result.filter(a => a.status === 'scheduled' && a.appointment_date >= today);
      } else if (this.activeTab === 'completed') {
        result = result.filter(a => a.status === 'completed');
      } else if (this.activeTab === 'cancelled') {
        result = result.filter(a => a.status === 'cancelled');
      }

      result.sort((a, b) => {
        if (this.activeTab === 'upcoming') {
          return a.appointment_date.localeCompare(b.appointment_date);
        }
        return b.appointment_date.localeCompare(a.appointment_date);
      });

      return result;
    },
    emptyMessage() {
      switch (this.activeTab) {
        case 'upcoming': return 'No upcoming appointments';
        case 'completed': return 'No completed appointments';
        case 'cancelled': return 'No cancelled appointments';
        default: return 'No appointments found';
      }
    }
  },
  methods: {
    async fetchAppointments() {
      try {
        this.loading = true;
        const res = await api.get('/patient/appointments');
        this.appointments = res.data?.data?.appointments || [];
      } catch (e) {
        console.error('Failed to fetch appointments:', e);
      } finally {
        this.loading = false;
      }
    },

    getCount(tab) {
      const today = new Date().toISOString().split('T')[0];
      switch (tab) {
        case 'upcoming':
          return this.appointments.filter(a => a.status === 'scheduled' && a.appointment_date >= today).length;
        case 'completed':
          return this.appointments.filter(a => a.status === 'completed').length;
        case 'cancelled':
          return this.appointments.filter(a => a.status === 'cancelled').length;
        default:
          return this.appointments.length;
      }
    },

    getDayOfMonth(date) {
      return new Date(date).getDate();
    },

    getMonth(date) {
      return new Date(date).toLocaleDateString('en-IN', { month: 'short' });
    },

    formatTime(time) {
      if (!time) return '';
      const [h, m] = time.split(':');
      const hour = parseInt(h);
      return `${hour % 12 || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    },

    formatStatus(status) {
      return status?.charAt(0).toUpperCase() + status?.slice(1).replace('_', ' ');
    },

    getStatusClass(status) {
      const classes = {
        'scheduled': 'bg-primary-subtle text-primary',
        'completed': 'bg-success-subtle text-success',
        'cancelled': 'bg-danger-subtle text-danger',
        'no_show': 'bg-warning-subtle text-warning'
      };
      return classes[status] || 'bg-secondary-subtle text-secondary';
    },

    getStatusIcon(status) {
      const icons = {
        'scheduled': 'bi bi-clock',
        'completed': 'bi bi-check-circle',
        'cancelled': 'bi bi-x-circle',
        'no_show': 'bi bi-exclamation-circle'
      };
      return icons[status] || 'bi bi-question-circle';
    },

    isUpcoming(row) {
      const today = new Date().toISOString().split('T')[0];
      return row.status === 'scheduled' && row.appointment_date >= today;
    },

    confirmCancel(apt) {
      this.selectedAppointment = apt;
      this.$refs.cancelModal.show();
    },

    async cancelAppointment() {
      if (!this.selectedAppointment) return;
      
      try {
        this.cancelling = true;
        await api.put(`/patient/appointments/${this.selectedAppointment.id}/cancel`);
        this.$refs.cancelModal.hide();
        this.fetchAppointments();
      } catch (e) {
        alert(e.response?.data?.message || 'Failed to cancel appointment');
      } finally {
        this.cancelling = false;
      }
    },

    openReschedule(apt) {
      this.selectedAppointment = apt;
      this.$refs.rescheduleModal.show();
    },

    onRescheduled() {
      this.fetchAppointments();
    },

    openEditNotes(apt) {
      this.selectedAppointment = apt;
      this.editingNotes = apt.booking_notes || '';
      this.notesModal.show();
    },

    async saveNotes() {
      if (!this.selectedAppointment) return;

      try {
        this.savingNotes = true;
        await api.put(`/patient/appointments/${this.selectedAppointment.id}/notes`, {
          booking_notes: this.editingNotes
        });
        this.notesModal.hide();
        this.fetchAppointments();
      } catch (e) {
        console.error('Failed to save notes:', e);
        alert(e.response?.data?.message || 'Failed to update notes');
      } finally {
        this.savingNotes = false;
      }
    },

    async viewRecord(apt) {
      this.loadingModal.show();

      try {
        const res = await api.get(`/patient/records/${apt.id - 1}`);
        const record = res.data?.data?.record;
        
        this.loadingModal.hide();

        if (record) {
          this.selectedRecord = {
            ...record,
            appointment_date: apt.appointment_date,
            appointment_time: apt.appointment_time,
            notes: record.treatment_notes,
            prescription_items: record.prescription_items || []
          };
          setTimeout(() => {
            this.$refs.recordModal.show();
          }, 200);
        } else {
          this.noRecordModal.show();
        }
      } catch (e) {
        console.error('Failed to fetch record:', e);
        this.loadingModal.hide();
        this.noRecordModal.show();
      }
    }
  },
  mounted() {
    this.fetchAppointments();
    this.loadingModal = new Modal(this.$refs.loadingModal);
    this.noRecordModal = new Modal(this.$refs.noRecordModal);
    this.notesModal = new Modal(this.$refs.notesModal);
  }
};
</script>