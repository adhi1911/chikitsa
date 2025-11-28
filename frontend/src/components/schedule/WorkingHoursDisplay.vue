<template>
  <div>
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-0 py-3">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-clock me-2 text-success"></i>Working Hours
        </h5>
      </div>
      <div class="card-body">
        <LoadingSpinner v-if="loading" size="sm" text="Loading schedule..." />
        
        <EmptyState 
          v-else-if="!workingHours || workingHours.length === 0"
          icon="bi bi-calendar-x"
          message="No working hours configured"
        >
          <p class="text-muted small">Please contact administration to set up your schedule.</p>
        </EmptyState>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Day</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="schedule in sortedWorkingHours" :key="schedule.id">
                <td>
                  <span class="fw-medium">{{ schedule.day_name || getDayName(schedule.day_of_week) }}</span>
                </td>
                <td>
                  <i class="bi bi-sun text-warning me-1"></i>
                  {{ formatTime(schedule.start_time) }}
                </td>
                <td>
                  <i class="bi bi-moon text-primary me-1"></i>
                  {{ formatTime(schedule.end_time) }}
                </td>
                <td>
                  <span class="badge bg-success-subtle text-success">Active</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Weekly Overview -->
    <div class="card border-0 shadow-sm mt-4">
      <div class="card-header bg-white border-0 py-3">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-eye me-2 text-primary"></i>Weekly Overview
        </h5>
      </div>
      <div class="card-body">
        <div class="row g-2">
          <div v-for="day in weekOverview" :key="day.value" class="col">
            <div 
              class="text-center p-3 rounded-3"
              :class="getDayClass(day)"
            >
              <div class="small fw-medium mb-1">{{ day.short }}</div>
              <div class="small">{{ day.dateStr }}</div>
              
              <!-- Has unavailability -->
              <div v-if="day.unavailable" class="small text-danger mt-1">
                <i class="bi bi-x-circle me-1"></i>
                {{ day.unavailable.isFullDay ? 'Unavailable' : 'Partial' }}
              </div>
              <!-- Working day -->
              <div v-else-if="day.schedule" class="small text-success mt-1">
                {{ formatTime(day.schedule.start_time) }}
                <br>
                {{ formatTime(day.schedule.end_time) }}
              </div>
              <!-- Off day -->
              <div v-else class="small text-muted mt-1">Off</div>
            </div>
          </div>
        </div>

        <!-- Upcoming Unavailabilities Legend -->
        <div v-if="upcomingUnavailabilities.length > 0" class="mt-3 pt-3 border-top">
          <small class="text-muted fw-medium">Upcoming Unavailabilities:</small>
          <div class="d-flex flex-wrap gap-2 mt-2">
            <span 
              v-for="u in upcomingUnavailabilities" 
              :key="u.id"
              class="badge bg-danger-subtle text-danger"
            >
              {{ formatDateShort(u.start_datetime) }}
              <span v-if="u.reason" class="ms-1">({{ u.reason }})</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Note -->
    <div class="alert alert-info mt-4">
      <i class="bi bi-info-circle me-2"></i>
      <small>Working hours are managed by hospital administration. Contact your admin to request changes.</small>
    </div>
  </div>
</template>

<script>
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import EmptyState from '@/components/common/EmptyState.vue';

export default {
  name: 'WorkingHoursDisplay',
  components: { LoadingSpinner, EmptyState },
  props: {
    workingHours: { type: Array, default: () => [] },
    unavailabilities: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  data() {
    return {
      weekDays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    };
  },
  computed: {
    sortedWorkingHours() {
      if (!this.workingHours) return [];
      return [...this.workingHours].sort((a, b) => a.day_of_week - b.day_of_week);
    },
    
    // Generate this week's overview with dates
    weekOverview() {
      const today = new Date();
      const monday = new Date(today);
      const dayOfWeek = today.getDay();
      const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Adjust to Monday
      monday.setDate(today.getDate() + diff);

      return this.weekDays.map((short, index) => {
        const date = new Date(monday);
        date.setDate(monday.getDate() + index);
        
        return {
          value: index,
          short,
          date,
          dateStr: date.getDate() + '/' + (date.getMonth() + 1),
          schedule: this.getDaySchedule(index),
          unavailable: this.getUnavailabilityForDate(date)
        };
      });
    },

    upcomingUnavailabilities() {
      if (!this.unavailabilities) return [];
      const now = new Date();
      return this.unavailabilities
        .filter(u => new Date(u.end_datetime) >= now)
        .slice(0, 5); // Show max 5
    }
  },
  methods: {
    getDayName(dayOfWeek) {
      const names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      return names[dayOfWeek] || '';
    },
    
    getDaySchedule(dayOfWeek) {
      if (!this.workingHours) return null;
      return this.workingHours.find(wh => wh.day_of_week === dayOfWeek) || null;
    },

    getUnavailabilityForDate(date) {
      if (!this.unavailabilities) return null;
      
      const dateStr = date.toISOString().split('T')[0];
      
      for (const u of this.unavailabilities) {
        const start = new Date(u.start_datetime);
        const end = new Date(u.end_datetime);
        
        // Check if date falls within unavailability range
        const startDate = start.toISOString().split('T')[0];
        const endDate = end.toISOString().split('T')[0];
        
        if (dateStr >= startDate && dateStr <= endDate) {
          const isFullDay = start.getHours() === 0 && end.getHours() === 23;
          return { ...u, isFullDay };
        }
      }
      return null;
    },

    getDayClass(day) {
      if (day.unavailable) {
        return day.unavailable.isFullDay ? 'bg-danger-subtle' : 'bg-warning-subtle';
      }
      if (day.schedule) {
        return 'bg-success-subtle';
      }
      return 'bg-light';
    },
    
    formatTime(time) {
      if (!time) return '';
      const [hours, minutes] = time.split(':');
      const h = parseInt(hours);
      return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
    },

    formatDateShort(datetime) {
      return new Date(datetime).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    }
  }
};
</script>