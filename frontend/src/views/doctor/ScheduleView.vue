<template>
  <div class="schedule-view">
    <PageHeader 
      title="My Schedule" 
      subtitle="View your working hours and manage availability"
    />

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'weekly' }" @click="activeTab = 'weekly'">
          <i class="bi bi-calendar-week me-2"></i>Weekly Schedule
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'unavailability' }" @click="activeTab = 'unavailability'">
          <i class="bi bi-calendar-x me-2"></i>Unavailability
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'today' }" @click="activeTab = 'today'">
          <i class="bi bi-calendar-day me-2"></i>Today's Schedule
        </button>
      </li>
    </ul>

    <!-- Weekly Schedule Tab -->
    <div v-show="activeTab === 'weekly'">
    <WorkingHoursDisplay 
        :working-hours="workingHours" 
        :unavailabilities="unavailabilities"
        :loading="loadingSchedule" 
    />
    </div>

    <!-- Unavailability Tab (Inline) -->
    <div v-show="activeTab === 'unavailability'">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
          <h5 class="mb-0 fw-semibold">
            <i class="bi bi-calendar-x me-2 text-danger"></i>Unavailable Dates
          </h5>
          <button class="btn btn-danger btn-sm" @click="$refs.unavailabilityModal.show()">
            <i class="bi bi-plus-lg me-1"></i>Add
          </button>
        </div>
        <div class="card-body">
          <LoadingSpinner v-if="loadingUnavailability" size="sm" />
          
          <div v-else-if="unavailabilities.length === 0" class="text-center py-4">
            <i class="bi bi-calendar-check text-muted fs-1"></i>
            <p class="text-muted mt-2 mb-0">No unavailabilities scheduled</p>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Reason</th>
                  <th width="80"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in unavailabilities" :key="item.id">
                  <td>
                    <strong>{{ formatDate(item.start_datetime) }}</strong>
                  </td>
                  <td>
                    <span class="badge" :class="isFullDay(item) ? 'bg-danger-subtle text-danger' : 'bg-warning-subtle text-warning'">
                      {{ isFullDay(item) ? 'Full Day' : formatTimeRange(item) }}
                    </span>
                  </td>
                  <td class="text-muted">{{ item.reason || '-' }}</td>
                  <td>
                    <button 
                      class="btn btn-sm btn-outline-danger"
                      @click="confirmDelete(item)"
                      :disabled="isPast(item)"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Schedule Tab -->
    <div v-show="activeTab === 'today'">
      <TodaySchedule :working-hours="workingHours" :appointments="todayAppointments" :loading="loadingToday" />
    </div>

    <!-- Modals -->
    <UnavailabilityModal ref="unavailabilityModal" :loading="saving" @save="saveUnavailability" />
    
    <ConfirmModal
      ref="deleteModal"
      title="Remove Unavailability"
      message="Remove this unavailability? You will be available for appointments."
      variant="danger"
      confirm-text="Remove"
      :loading="deleting"
      @confirm="deleteUnavailability"
    />
  </div>
</template>

<script>
import api from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import WorkingHoursDisplay from '@/components/schedule/WorkingHoursDisplay.vue';
import TodaySchedule from '@/components/schedule/TodaySchedule.vue';
import UnavailabilityModal from '@/components/schedule/UnavailabilityModal.vue';

export default {
  name: 'ScheduleView',
  components: {
    PageHeader,
    LoadingSpinner,
    ConfirmModal,
    WorkingHoursDisplay,
    TodaySchedule,
    UnavailabilityModal
  },
  data() {
    return {
      activeTab: 'weekly',
      loadingSchedule: true,
      loadingUnavailability: true,
      loadingToday: true,
      saving: false,
      deleting: false,
      workingHours: [],
      unavailabilities: [],
      todayAppointments: [],
      deleteTarget: null
    };
  },
  methods: {
    async fetchWorkingHours() {
      try {
        this.loadingSchedule = true;
        const res = await api.get('/doctor/working-hours');
        this.workingHours = res.data.data?.working_hours || [];
      } catch (e) {
        console.error(e);
      } finally {
        this.loadingSchedule = false;
      }
    },

    async fetchUnavailabilities() {
      try {
        this.loadingUnavailability = true;
        const res = await api.get('/doctor/unavailability');
        this.unavailabilities = res.data.data?.unavailability || [];
      } catch (e) {
        console.error(e);
      } finally {
        this.loadingUnavailability = false;
      }
    },

    async fetchTodayAppointments() {
      try {
        this.loadingToday = true;
        const today = new Date().toISOString().split('T')[0];
        const res = await api.get('/doctor/appointments', { params: { start_date: today, end_date: today } });
        this.todayAppointments = (res.data.data?.appointments || []).sort((a, b) => a.appointment_time.localeCompare(b.appointment_time));
      } catch (e) {
        console.error(e);
      } finally {
        this.loadingToday = false;
      }
    },

    async saveUnavailability(data) {
      try {
        this.saving = true;
        await api.post('/doctor/unavailability', data);
        this.$refs.unavailabilityModal.hide();
        await this.fetchUnavailabilities();
      } catch (e) {
        alert(e.response?.data?.message || 'Failed to save');
      } finally {
        this.saving = false;
      }
    },

    confirmDelete(item) {
      this.deleteTarget = item;
      this.$refs.deleteModal.show();
    },

    async deleteUnavailability() {
      try {
        this.deleting = true;
        await api.delete(`/doctor/unavailability/${this.deleteTarget.id}`);
        this.$refs.deleteModal.hide();
        await this.fetchUnavailabilities();
      } catch (e) {
        alert(e.response?.data?.message || 'Failed to delete');
      } finally {
        this.deleting = false;
      }
    },

    // Helpers
    formatDate(datetime) {
      return new Date(datetime).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    },
    
    isFullDay(item) {
      const start = new Date(item.start_datetime);
      const end = new Date(item.end_datetime);
      return start.getHours() === 0 && end.getHours() === 23;
    },
    
    formatTimeRange(item) {
      const fmt = (d) => new Date(d).toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit' });
      return `${fmt(item.start_datetime)} - ${fmt(item.end_datetime)}`;
    },
    
    isPast(item) {
      return new Date(item.end_datetime) < new Date();
    }
  },

  watch: {
    activeTab(tab) {
      if (tab === 'today') this.fetchTodayAppointments();
    }
  },

  mounted() {
    this.fetchWorkingHours();
    this.fetchUnavailabilities();
    this.fetchTodayAppointments();
  }
};
</script>

<style scoped>
.nav-tabs .nav-link {
  color: #6c757d;
  border: none;
  border-bottom: 2px solid transparent;
}
.nav-tabs .nav-link.active {
  color: #198754;
  border-bottom-color: #198754;
  background: transparent;
}
</style>