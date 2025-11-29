<template>
  <div class="appointment-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1 fw-bold">
          <i class="bi bi-calendar-check me-2 text-primary"></i>Appointments
        </h2>
        <p class="text-muted mb-0">Manage and track all appointments</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary" @click="exportAppointments">
          <i class="bi bi-download me-2"></i>Export
        </button>
        <button class="btn btn-primary" @click="refreshData">
          <i class="bi bi-arrow-clockwise me-2"></i>Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-primary-subtle rounded-3 p-3 me-3">
              <i class="bi bi-calendar-event fs-4 text-primary"></i>
            </div>
            <div>
              <h3 class="fw-bold mb-0">{{ stats.total }}</h3>
              <small class="text-muted">Total</small>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-info-subtle rounded-3 p-3 me-3">
              <i class="bi bi-clock fs-4 text-info"></i>
            </div>
            <div>
              <h3 class="fw-bold mb-0">{{ stats.scheduled }}</h3>
              <small class="text-muted">Scheduled</small>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-success-subtle rounded-3 p-3 me-3">
              <i class="bi bi-check-circle fs-4 text-success"></i>
            </div>
            <div>
              <h3 class="fw-bold mb-0">{{ stats.completed }}</h3>
              <small class="text-muted">Completed</small>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body d-flex align-items-center">
            <div class="stat-icon bg-danger-subtle rounded-3 p-3 me-3">
              <i class="bi bi-x-circle fs-4 text-danger"></i>
            </div>
            <div>
              <h3 class="fw-bold mb-0">{{ stats.cancelled }}</h3>
              <small class="text-muted">Cancelled</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Search -->
          <div class="col-md-3">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search patient or doctor..."
                v-model="searchQuery"
              >
            </div>
          </div>

          <!-- Status Filter -->
          <div class="col-md-2">
            <select class="form-select" v-model="filterStatus">
              <option value="">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="no_show">No Show</option>
            </select>
          </div>

          <!-- Doctor Filter -->
          <div class="col-md-2">
            <select class="form-select" v-model="filterDoctor">
              <option value="">All Doctors</option>
              <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                Dr. {{ doctor.first_name }} {{ doctor.last_name }}
              </option>
            </select>
          </div>

          <!-- Date Range -->
          <div class="col-md-2">
            <input 
              type="date" 
              class="form-control" 
              v-model="filterStartDate"
              placeholder="Start Date"
            >
          </div>
          <div class="col-md-2">
            <input 
              type="date" 
              class="form-control" 
              v-model="filterEndDate"
              placeholder="End Date"
            >
          </div>

          <!-- Reset -->
          <div class="col-md-1">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters" title="Reset">
              <i class="bi bi-arrow-counterclockwise"></i>
            </button>
          </div>
        </div>

        <!-- Quick Filters -->
        <div class="mt-3 d-flex gap-2 flex-wrap">
          <button 
            class="btn btn-sm"
            :class="quickFilter === 'today' ? 'btn-primary' : 'btn-outline-primary'"
            @click="setQuickFilter('today')"
          >
            Today
          </button>
          <button 
            class="btn btn-sm"
            :class="quickFilter === 'tomorrow' ? 'btn-primary' : 'btn-outline-primary'"
            @click="setQuickFilter('tomorrow')"
          >
            Tomorrow
          </button>
          <button 
            class="btn btn-sm"
            :class="quickFilter === 'week' ? 'btn-primary' : 'btn-outline-primary'"
            @click="setQuickFilter('week')"
          >
            This Week
          </button>
          <button 
            class="btn btn-sm"
            :class="quickFilter === 'month' ? 'btn-primary' : 'btn-outline-primary'"
            @click="setQuickFilter('month')"
          >
            This Month
          </button>
          <button 
            class="btn btn-sm"
            :class="quickFilter === 'pending' ? 'btn-warning' : 'btn-outline-warning'"
            @click="setQuickFilter('pending')"
          >
            Pending Action
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading appointments...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger border-0 shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchAppointments">Retry</button>
    </div>

    <!-- Appointments Table -->
    <div v-else-if="filteredAppointments.length > 0" class="card border-0 shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  v-model="selectAll"
                  @change="toggleSelectAll"
                >
              </th>
              <th @click="sortTable('appointment_date')" class="sortable">
                Date & Time
                <i class="bi" :class="getSortIcon('appointment_date')"></i>
              </th>
              <th @click="sortTable('patient_name')" class="sortable">
                Patient
                <i class="bi" :class="getSortIcon('patient_name')"></i>
              </th>
              <th @click="sortTable('doctor_name')" class="sortable">
                Doctor
                <i class="bi" :class="getSortIcon('doctor_name')"></i>
              </th>
              <th>Department</th>
              <th @click="sortTable('status')" class="sortable">
                Status
                <i class="bi" :class="getSortIcon('status')"></i>
              </th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="appointment in paginatedAppointments" 
              :key="appointment.id"
              :class="getRowClass(appointment)"
            >
              <!-- Checkbox -->
              <td>
                <input 
                  type="checkbox" 
                  class="form-check-input"
                  v-model="selectedAppointments"
                  :value="appointment.id"
                >
              </td>

              <!-- Date & Time -->
              <td>
                <div class="d-flex align-items-center">
                  <div class="date-badge me-3 text-center">
                    <div class="fw-bold text-primary">{{ formatDay(appointment.appointment_date) }}</div>
                    <small class="text-muted">{{ formatMonth(appointment.appointment_date) }}</small>
                  </div>
                  <div>
                    <div class="fw-semibold">{{ formatTime(appointment.appointment_time) }}</div>
                    <small class="text-muted">{{ getRelativeDate(appointment.appointment_date) }}</small>
                  </div>
                </div>
              </td>

              <!-- Patient -->
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar bg-primary-subtle rounded-circle me-2">
                    <span class="text-primary fw-bold small">
                      {{ getInitials(appointment.patient_name) }}
                    </span>
                  </div>
                  <div>
                    <div class="fw-medium">{{ appointment.patient_name }}</div>
                    <small class="text-muted">ID: {{ appointment.patient_id }}</small>
                  </div>
                </div>
              </td>

              <!-- Doctor -->
              <td>
                <div>
                  <div class="fw-medium">Dr. {{ appointment.doctor_name }}</div>
                  <small class="text-muted">{{ appointment.specialization || '-' }}</small>
                </div>
              </td>

              <!-- Department -->
              <td>
                <span class="badge bg-light text-dark">
                  {{ appointment.department || '-' }}
                </span>
              </td>

              <!-- Status -->
              <td>
                <span class="badge" :class="getStatusBadgeClass(appointment.status)">
                  <i class="bi me-1" :class="getStatusIcon(appointment.status)"></i>
                  {{ formatStatus(appointment.status) }}
                </span>
              </td>

              <!-- Actions -->
              <td class="text-center">
                <div class="btn-group">
                  <button 
                    class="btn btn-sm btn-outline-info"
                    @click="viewAppointment(appointment)"
                    title="View Details"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    v-if="appointment.status === 'scheduled'"
                    @click="confirmCancel(appointment)"
                    title="Cancel"
                  >
                    <i class="bi bi-x-lg"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-warning"
                    v-if="appointment.status === 'scheduled'"
                    @click="markNoShow(appointment)"
                    title="Mark No Show"
                  >
                    <i class="bi bi-person-x"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    v-if="appointment.has_medical_record"
                    @click="viewMedicalRecord(appointment)"
                    title="View Medical Record"
                  >
                    <i class="bi bi-file-medical"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination & Bulk Actions -->
      <div class="card-footer bg-white border-0">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-3">
            <small class="text-muted">
              Showing {{ paginationStart }} - {{ paginationEnd }} of {{ filteredAppointments.length }}
            </small>
            
            <!-- Bulk Actions -->
            <div v-if="selectedAppointments.length > 0" class="d-flex gap-2">
              <span class="badge bg-primary">{{ selectedAppointments.length }} selected</span>
              <button class="btn btn-sm btn-outline-danger" @click="bulkCancel">
                <i class="bi bi-x-circle me-1"></i>Cancel Selected
              </button>
            </div>
          </div>

          <!-- Pagination -->
          <nav>
            <ul class="pagination pagination-sm mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage--">
                  <i class="bi bi-chevron-left"></i>
                </a>
              </li>
              <li 
                class="page-item" 
                v-for="page in displayedPages" 
                :key="page"
                :class="{ active: currentPage === page, disabled: page === '...' }"
              >
                <a class="page-link" href="#" @click.prevent="page !== '...' && (currentPage = page)">
                  {{ page }}
                </a>
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
      <i class="bi bi-calendar-x display-1 text-muted opacity-50"></i>
      <h4 class="mt-3 text-muted">No Appointments Found</h4>
      <p class="text-muted">{{ getEmptyMessage() }}</p>
      <button class="btn btn-outline-primary" @click="resetFilters">Clear Filters</button>
    </div>

    <!-- View Appointment Modal -->
    <div class="modal fade" id="viewModal" tabindex="-1" ref="viewModal">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0 pb-0">
            <div>
              <h5 class="modal-title fw-semibold">
                <i class="bi bi-calendar-check me-2 text-primary"></i>Appointment Details
              </h5>
              <small class="text-muted">ID: {{ selectedAppointment?.id }}</small>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body pt-4" v-if="selectedAppointment">
            <!-- Status Banner -->
            <div 
              class="alert mb-4" 
              :class="getStatusAlertClass(selectedAppointment.status)"
            >
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <i class="bi me-2" :class="getStatusIcon(selectedAppointment.status)"></i>
                  <strong>{{ formatStatus(selectedAppointment.status) }}</strong>
                </div>
                <small>{{ formatFullDate(selectedAppointment.appointment_date) }} at {{ formatTime(selectedAppointment.appointment_time) }}</small>
              </div>
            </div>

            <div class="row g-4">
              <!-- Patient Info -->
              <div class="col-md-6">
                <div class="card bg-light border-0">
                  <div class="card-body">
                    <h6 class="text-muted mb-3">
                      <i class="bi bi-person me-2"></i>Patient Information
                    </h6>
                    <div class="d-flex align-items-center mb-3">
                      <div class="avatar-lg bg-primary-subtle rounded-circle me-3">
                        <span class="text-primary fw-bold">
                          {{ getInitials(selectedAppointment.patient_name) }}
                        </span>
                      </div>
                      <div>
                        <h6 class="mb-0">{{ selectedAppointment.patient_name }}</h6>
                        <small class="text-muted">Patient ID: {{ selectedAppointment.patient_id }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Doctor Info -->
              <div class="col-md-6">
                <div class="card bg-light border-0">
                  <div class="card-body">
                    <h6 class="text-muted mb-3">
                      <i class="bi bi-person-badge me-2"></i>Doctor Information
                    </h6>
                    <div class="d-flex align-items-center mb-3">
                      <div class="avatar-lg bg-success-subtle rounded-circle me-3">
                        <span class="text-success fw-bold">
                          {{ getInitials(selectedAppointment.doctor_name) }}
                        </span>
                      </div>
                      <div>
                        <h6 class="mb-0">Dr. {{ selectedAppointment.doctor_name }}</h6>
                        <small class="text-muted">{{ selectedAppointment.department }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Appointment Details -->
              <div class="col-12">
                <div class="row g-3">
                  <div class="col-md-4">
                    <label class="form-label text-muted small fw-semibold">DATE</label>
                    <p class="mb-0 fw-medium">{{ formatFullDate(selectedAppointment.appointment_date) }}</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label text-muted small fw-semibold">TIME</label>
                    <p class="mb-0 fw-medium">{{ formatTime(selectedAppointment.appointment_time) }}</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label text-muted small fw-semibold">CONSULTATION FEE</label>
                    <p class="mb-0 fw-medium">₹{{ selectedAppointment.consultation_fee || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Booking Notes -->
              <div class="col-12" v-if="selectedAppointment.booking_notes">
                <label class="form-label text-muted small fw-semibold">BOOKING NOTES</label>
                <div class="bg-light rounded p-3">
                  <p class="mb-0">{{ selectedAppointment.booking_notes }}</p>
                </div>
              </div>

              <!-- Timeline -->
              <div class="col-12">
                <label class="form-label text-muted small fw-semibold">TIMELINE</label>
                <div class="timeline">
                  <div class="timeline-item">
                    <div class="timeline-marker bg-primary"></div>
                    <div class="timeline-content">
                      <small class="text-muted">Created</small>
                      <p class="mb-0">{{ formatDateTime(selectedAppointment.created_at) }}</p>
                    </div>
                  </div>
                  <div class="timeline-item" v-if="selectedAppointment.updated_at">
                    <div class="timeline-marker bg-info"></div>
                    <div class="timeline-content">
                      <small class="text-muted">Last Updated</small>
                      <p class="mb-0">{{ formatDateTime(selectedAppointment.updated_at) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Close</button>
            <button 
              type="button" 
              class="btn btn-danger"
              v-if="selectedAppointment?.status === 'scheduled'"
              @click="cancelFromModal"
            >
              <i class="bi bi-x-lg me-2"></i>Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Confirmation Modal -->
    <div class="modal fade" id="cancelModal" tabindex="-1" ref="cancelModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-semibold text-danger">
              <i class="bi bi-exclamation-triangle me-2"></i>Cancel Appointment
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to cancel this appointment?</p>
            <div class="bg-light rounded p-3 mb-3">
              <div class="d-flex justify-content-between">
                <span>Patient:</span>
                <strong>{{ selectedAppointment?.patient_name }}</strong>
              </div>
              <div class="d-flex justify-content-between">
                <span>Doctor:</span>
                <strong>Dr. {{ selectedAppointment?.doctor_name }}</strong>
              </div>
              <div class="d-flex justify-content-between">
                <span>Date:</span>
                <strong>{{ formatFullDate(selectedAppointment?.appointment_date) }}</strong>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Cancellation Reason</label>
              <textarea 
                class="form-control" 
                v-model="cancelReason" 
                rows="2"
                placeholder="Enter reason for cancellation..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Keep Appointment</button>
            <button type="button" class="btn btn-danger" @click="cancelAppointment" :disabled="cancelling">
              <span v-if="cancelling" class="spinner-border spinner-border-sm me-2"></span>
              Cancel Appointment
            </button>
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
  name: 'AppointmentListView',
  data() {
    return {
      appointments: [],
      doctors: [],
      loading: true,
      error: null,
      
      // Filters
      searchQuery: '',
      filterStatus: '',
      filterDoctor: '',
      filterStartDate: '',
      filterEndDate: '',
      quickFilter: '',
      
      // Sorting
      sortField: 'appointment_date',
      sortOrder: 'desc',
      
      // Pagination
      currentPage: 1,
      perPage: 15,
      
      // Selection
      selectedAppointments: [],
      selectAll: false,
      
      // Modals
      selectedAppointment: null,
      cancelReason: '',
      cancelling: false,
      medicalRecord: null,
      loadingRecord: false,
      
      modals: {}
    };
  },
  computed: {
    stats() {
      return {
        total: this.appointments.length,
        scheduled: this.appointments.filter(a => a.status === 'scheduled').length,
        completed: this.appointments.filter(a => a.status === 'completed').length,
        cancelled: this.appointments.filter(a => a.status === 'cancelled').length
      };
    },
    filteredAppointments() {
      let result = [...this.appointments];

      // Search
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(a => 
          a.patient_name?.toLowerCase().includes(query) ||
          a.doctor_name?.toLowerCase().includes(query)
        );
      }

      // Status filter
      if (this.filterStatus) {
        result = result.filter(a => a.status === this.filterStatus);
      }

      // Doctor filter
      if (this.filterDoctor) {
        result = result.filter(a => a.doctor_id === this.filterDoctor);
      }

      // Date filters
      if (this.filterStartDate) {
        result = result.filter(a => a.appointment_date >= this.filterStartDate);
      }
      if (this.filterEndDate) {
        result = result.filter(a => a.appointment_date <= this.filterEndDate);
      }

      // Sort
      result.sort((a, b) => {
        let aVal = a[this.sortField];
        let bVal = b[this.sortField];
        
        if (this.sortField === 'appointment_date') {
          aVal = `${a.appointment_date} ${a.appointment_time}`;
          bVal = `${b.appointment_date} ${b.appointment_time}`;
        }
        
        if (this.sortOrder === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });

      return result;
    },
    totalPages() {
      return Math.ceil(this.filteredAppointments.length / this.perPage);
    },
    paginatedAppointments() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredAppointments.slice(start, start + this.perPage);
    },
    paginationStart() {
      return (this.currentPage - 1) * this.perPage + 1;
    },
    paginationEnd() {
      return Math.min(this.currentPage * this.perPage, this.filteredAppointments.length);
    },
    displayedPages() {
      const pages = [];
      const total = this.totalPages;
      const current = this.currentPage;

      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        if (current <= 3) {
          pages.push(1, 2, 3, 4, '...', total);
        } else if (current >= total - 2) {
          pages.push(1, '...', total - 3, total - 2, total - 1, total);
        } else {
          pages.push(1, '...', current - 1, current, current + 1, '...', total);
        }
      }
      return pages;
    }
  },
  methods: {
    async fetchAppointments() {
      try {
        this.loading = true;
        this.error = null;

        const params = new URLSearchParams();
        if (this.filterStartDate) params.append('start_date', this.filterStartDate);
        if (this.filterEndDate) params.append('end_date', this.filterEndDate);
        if (this.filterStatus) params.append('status', this.filterStatus);
        if (this.filterDoctor) params.append('doctor_id', this.filterDoctor);

        const response = await api.get(`/admin/appointments?${params.toString()}`);
        if (response.data.status === 'success') {
          this.appointments = response.data.data.appointments;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch appointments';
      } finally {
        this.loading = false;
      }
    },
    async fetchDoctors() {
      try {
        const response = await api.get('/admin/doctors');
        if (response.data.status === 'success') {
          this.doctors = response.data.data.doctors;
        }
      } catch (error) {
        console.error('Failed to fetch doctors:', error);
      }
    },
    refreshData() {
      this.fetchAppointments();
    },

    // Formatting
    formatDay(date) {
      return new Date(date).getDate();
    },
    formatMonth(date) {
      return new Date(date).toLocaleDateString('en-US', { month: 'short' });
    },
    formatTime(time) {
      if (!time) return '-';
      const [hours, minutes] = time.split(':');
      const h = parseInt(hours);
      const ampm = h >= 12 ? 'PM' : 'AM';
      const h12 = h % 12 || 12;
      return `${h12}:${minutes} ${ampm}`;
    },
    formatFullDate(date) {
      if (!date) return '-';
      return new Date(date).toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    formatDateTime(datetime) {
      if (!datetime) return '-';
      return new Date(datetime).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    formatStatus(status) {
      const map = {
        scheduled: 'Scheduled',
        completed: 'Completed',
        cancelled: 'Cancelled',
        no_show: 'No Show'
      };
      return map[status] || status;
    },
    getRelativeDate(date) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const appointmentDate = new Date(date);
      appointmentDate.setHours(0, 0, 0, 0);
      
      const diff = Math.floor((appointmentDate - today) / (1000 * 60 * 60 * 24));
      
      if (diff === 0) return 'Today';
      if (diff === 1) return 'Tomorrow';
      if (diff === -1) return 'Yesterday';
      if (diff > 0) return `In ${diff} days`;
      return `${Math.abs(diff)} days ago`;
    },
    getInitials(name) {
      if (!name) return '?';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },

    // Styling
    getStatusBadgeClass(status) {
      const classes = {
        scheduled: 'bg-info-subtle text-info',
        completed: 'bg-success-subtle text-success',
        cancelled: 'bg-danger-subtle text-danger',
        no_show: 'bg-warning-subtle text-warning'
      };
      return classes[status] || 'bg-secondary-subtle text-secondary';
    },
    getStatusIcon(status) {
      const icons = {
        scheduled: 'bi-clock',
        completed: 'bi-check-circle',
        cancelled: 'bi-x-circle',
        no_show: 'bi-person-x'
      };
      return icons[status] || 'bi-question-circle';
    },
    getStatusAlertClass(status) {
      const classes = {
        scheduled: 'alert-info',
        completed: 'alert-success',
        cancelled: 'alert-danger',
        no_show: 'alert-warning'
      };
      return classes[status] || 'alert-secondary';
    },
    getRowClass(appointment) {
      const today = new Date().toISOString().split('T')[0];
      if (appointment.appointment_date === today && appointment.status === 'scheduled') {
        return 'table-warning';
      }
      if (appointment.status === 'cancelled') {
        return 'table-light text-muted';
      }
      return '';
    },

    // Sorting
    sortTable(field) {
      if (this.sortField === field) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = field;
        this.sortOrder = 'asc';
      }
    },
    getSortIcon(field) {
      if (this.sortField !== field) return 'bi-chevron-expand';
      return this.sortOrder === 'asc' ? 'bi-chevron-up' : 'bi-chevron-down';
    },

    // Filters
    resetFilters() {
      this.searchQuery = '';
      this.filterStatus = '';
      this.filterDoctor = '';
      this.filterStartDate = '';
      this.filterEndDate = '';
      this.quickFilter = '';
      this.currentPage = 1;
      this.fetchAppointments();
    },
    setQuickFilter(filter) {
      const today = new Date();
      const todayStr = today.toISOString().split('T')[0];

      this.quickFilter = filter;
      this.filterStatus = '';

      switch (filter) {
        case 'today':
          this.filterStartDate = todayStr;
          this.filterEndDate = todayStr;
          break;
        case 'tomorrow':
          const tomorrow = new Date(today);
          tomorrow.setDate(tomorrow.getDate() + 1);
          const tomorrowStr = tomorrow.toISOString().split('T')[0];
          this.filterStartDate = tomorrowStr;
          this.filterEndDate = tomorrowStr;
          break;
        case 'week':
          const weekEnd = new Date(today);
          weekEnd.setDate(weekEnd.getDate() + 7);
          this.filterStartDate = todayStr;
          this.filterEndDate = weekEnd.toISOString().split('T')[0];
          break;
        case 'month':
          const monthEnd = new Date(today);
          monthEnd.setMonth(monthEnd.getMonth() + 1);
          this.filterStartDate = todayStr;
          this.filterEndDate = monthEnd.toISOString().split('T')[0];
          break;
        case 'pending':
          this.filterStatus = 'scheduled';
          this.filterStartDate = '';
          this.filterEndDate = '';
          break;
      }

      this.fetchAppointments();
    },
    getEmptyMessage() {
      if (this.searchQuery) return 'Try adjusting your search query';
      if (this.quickFilter) return 'No appointments match the selected filter';
      if (this.filterStatus) return `No ${this.filterStatus} appointments found`;
      return 'No appointments have been scheduled yet';
    },

    // Selection
    toggleSelectAll() {
      if (this.selectAll) {
        this.selectedAppointments = this.paginatedAppointments
          .filter(a => a.status === 'scheduled')
          .map(a => a.id);
      } else {
        this.selectedAppointments = [];
      }
    },

    // Actions
    viewAppointment(appointment) {
      this.selectedAppointment = appointment;
      this.modals.view.show();
    },
    confirmCancel(appointment) {
      this.selectedAppointment = appointment;
      this.cancelReason = '';
      this.modals.cancel.show();
    },
    cancelFromModal() {
      this.modals.view.hide();
      this.confirmCancel(this.selectedAppointment);
    },
    async cancelAppointment() {
      try {
        this.cancelling = true;
        await api.patch(`/admin/appointments/${this.selectedAppointment.id}/status`, {
          status: 'canceled',
          reason: this.cancelReason
        });
        this.modals.cancel.hide();
        await this.fetchAppointments();
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to cancel appointment');
      } finally {
        this.cancelling = false;
      }
    },
    async markNoShow(appointment) {
      if (!confirm('Mark this appointment as No Show?')) return;
      try {
        await api.patch(`/admin/appointments/${appointment.id}/status`, {
          status: 'no_show'
        });
        await this.fetchAppointments();
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update appointment');
      }
    },
    async bulkCancel() {
      if (!confirm(`Cancel ${this.selectedAppointments.length} appointments?`)) return;
      try {
        for (const id of this.selectedAppointments) {
          await api.patch(`/admin/appointments/${id}/status`, {
            status: 'cancelled',
            reason: 'Bulk cancellation by admin'
          });
        }
        this.selectedAppointments = [];
        this.selectAll = false;
        await this.fetchAppointments();
      } catch (error) {
        alert('Failed to cancel some appointments');
      }
    },
    async viewMedicalRecord(appointment) {
        this.selectedAppointment = appointment;
        this.medicalRecord = null;
        this.loadingRecord = true;
        this.modals.record.show();

        try {
            // Use the new dedicated route
            const response = await api.get(`/admin/appointments/${appointment.id}/record`);
            if (response.data.status === 'success') {
            this.medicalRecord = response.data.data.record;
            }
        } catch (error) {
            if (error.response?.status !== 404) {
            console.error('Failed to fetch medical record:', error);
            }
            this.medicalRecord = null;
        } finally {
            this.loadingRecord = false;
        }
    },
    exportAppointments() {
      // Simple CSV export
      const headers = ['ID', 'Date', 'Time', 'Patient', 'Doctor', 'Department', 'Status'];
      const rows = this.filteredAppointments.map(a => [
        a.id,
        a.appointment_date,
        a.appointment_time,
        a.patient_name,
        `Dr. ${a.doctor_name}`,
        a.department || '',
        a.status
      ]);

      const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `appointments_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    }
  },
  watch: {
    filterStatus() {
      this.currentPage = 1;
    },
    filterDoctor() {
      this.currentPage = 1;
    }
  },
  mounted() {
    this.fetchAppointments();
    this.fetchDoctors();

    // Initialize modals
    this.modals = {
      view: new Modal(this.$refs.viewModal),
      cancel: new Modal(this.$refs.cancelModal),
    };
  }
};
</script>

